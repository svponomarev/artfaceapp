#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === colorization.py: script for colorizing images using caffe neural network === """      
import os
import uuid
import numpy as np
import skimage.color as color
import matplotlib.pyplot as plt
import scipy.ndimage.interpolation as sni

from PIL import Image, ImageStat

import caffe
# load model files for caffe neural network https://github.com/richzhang/colorization
cur_dir = os.path.dirname(os.path.realpath(__file__))
prototxt = cur_dir + '/models/colorization_deploy_v2.prototxt'
caffemodel  = cur_dir + '/models/colorization_release_v2.caffemodel'
cluster_cntrs = cur_dir + '/resources/pts_in_hull.npy'

os.environ['GLOG_minloglevel'] = '2' # disable warnings from caffe

def detect_color_image(file, thumb_size=40, MSE_cutoff=80, adjust_color_bias=True):
    """checks if image monochrome or colored"""
    """ see https://stackoverflow.com/questions/20068945/detect-if-image-is-color-grayscale-or-black-and-white-with-python-pil """
    pil_img = Image.open(file)
    bands = pil_img.getbands()
    if bands == ('R','G','B') or bands== ('R','G','B','A'):
        thumb = pil_img.resize((thumb_size,thumb_size))
        SSE, bias = 0, [0,0,0]
        if adjust_color_bias:
            bias = ImageStat.Stat(thumb).mean[:3]
            bias = [b - sum(bias)/3 for b in bias ]
        for pixel in thumb.getdata():
            mu = sum(pixel)/3
            SSE += sum((pixel[i] - mu - bias[i])*(pixel[i] - mu - bias[i]) for i in [0,1,2])
        MSE = float(SSE)/(thumb_size*thumb_size)
        if MSE <= MSE_cutoff:
            #print "grayscale\t"
            #print "( MSE=",MSE,")"
            return 0
        else:
            #print "Color\t\t\t"
            #print "( MSE=",MSE,")"
            return 1
    elif len(bands)==1:
        #print "Black and white", bands
        return 0
    else:
        #print "Don't know...", bands
        return 1

def colorize_image(path, decade):
    """converting input image to monochrome or colorizing it depending on selected decade"""

    colorized_path = os.path.dirname(path) + "/" + str(uuid.uuid4()) + ".jpg" # path to image after colorization
  
    is_colored = detect_color_image(path)
    pil_img = Image.open(path)
    decade = int(decade)
    
    if is_colored:         
        if decade < 1950: # for earlier years images should be monochrome
            #print("Converting to monochrome")
            pil_img= pil_img.convert('L')
            pil_img.save(colorized_path, "JPEG")
        else:
            #print("No need to colorizing, exiting...") # skip colorization
            return path
    else: 
        if decade >= 1950:  # apply colorization for the later decades
            #print("Applying colorization...")
            neural_colorize(path, colorized_path)
        else:
            #print("Converting to monochrome") 
            pil_img= pil_img.convert('L')
            pil_img.save(colorized_path, "JPEG")

    return colorized_path


def neural_colorize(in_path, out_path):
    """colorize input image using caffe neural network"""
    caffe.set_mode_cpu() # using cpu mode
    #caffe.set_device(0)

    # Select desired model
    net = caffe.Net(prototxt, caffemodel, caffe.TEST)

    (H_in,W_in) = net.blobs['data_l'].data.shape[2:] # get input shape
    (H_out,W_out) = net.blobs['class8_ab'].data.shape[2:] # get output shape

    pts_in_hull = np.load(cluster_cntrs) # load cluster centers
    net.params['class8_ab'][0].data[:,:,0,0] = pts_in_hull.transpose((1,0)) # populate cluster centers as 1x1 convolution kernel
    # print 'Annealed-Mean Parameters populated'

    # load the original image
    img_rgb = caffe.io.load_image(in_path)

    img_lab = color.rgb2lab(img_rgb) # convert image to lab color space
    img_l = img_lab[:,:,0] # pull out L channel
    (H_orig,W_orig) = img_rgb.shape[:2] # original image size

    # create grayscale version of image (just for displaying)
    img_lab_bw = img_lab.copy()
    img_lab_bw[:,:,1:] = 0
    img_rgb_bw = color.lab2rgb(img_lab_bw)

    # resize image to network input size
    img_rs = caffe.io.resize_image(img_rgb,(H_in,W_in)) # resize image to network input size
    img_lab_rs = color.rgb2lab(img_rs)
    img_l_rs = img_lab_rs[:,:,0]

    net.blobs['data_l'].data[0,0,:,:] = img_l_rs-50 # subtract 50 for mean-centering
    net.forward() # run network

    ab_dec = net.blobs['class8_ab'].data[0,:,:,:].transpose((1,2,0)) # this is our result
    ab_dec_us = sni.zoom(ab_dec,(1.*H_orig/H_out,1.*W_orig/W_out,1)) # upsample to match size of original image L
    img_lab_out = np.concatenate((img_l[:,:,np.newaxis],ab_dec_us),axis=2) # concatenate with original image L
    img_rgb_out = (255*np.clip(color.lab2rgb(img_lab_out),0,1)).astype('uint8') # convert back to rgb

    plt.imsave(out_path, img_rgb_out)
