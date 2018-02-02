#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === photo_style_transfer.py: script for applying photo style transfer on image using filters === """    
import os
import uuid
import shutil
import inspect

from PIL import Image
from Naked.toolshed.shell import execute_js, muterun_js

from photo_style.instagram_filters.filters import *

js_path = "./app/stylization/photo_style/render_colors.js" # path to the Node.js script with part of the photo filters

def expand_rect_padding(img_path, padding_x, padding_top, padding_bottom, out_path):
    """places image into new canvas with paddings, useful for non-standard frames like polaroid"""
    pil_image_frame = Image.open(img_path)
    im_width, im_height = pil_image_frame.size  
    
    n_width = im_width + 2 * padding_x
    n_height = im_height + padding_top + padding_bottom
    
    old_size = (im_width, im_height)
    new_size = (n_width, n_height)
    new_im = Image.new("RGB", new_size, "white") 
    new_im.paste(pil_image_frame, ((new_size[0]-old_size[0])/2, padding_top)) # insert image into center of new canvas with vertical shift = padding_top 

    new_im.save(out_path, "JPEG")
    
def apply_photo_style(path, decade):
    """stylize image with photo filter according to selected decade"""
    flt_path = os.path.dirname(path) + "/" + str(uuid.uuid4()) + ".jpg"
    shutil.copyfile(path, flt_path) # make a copy of image because part of the filters change image in place
    f = None
    if decade <= 1930 or decade == 1950 or decade == 1970:
        success = execute_js(js_path, arguments='{} {} {}'.format(path, decade, flt_path)) # execute js rendering with Naked
    if decade == 1930:
        f = Thirties(flt_path)
    if decade == 1940:
        f = Gotham(flt_path)
    
    if decade == 1950 or decade == 1960: # for non-standard photo frames       
        padding_x = 80
        if decade == 1950: # kodachrome frame
            padding_top = 80
            padding_bottom = 240
        else: # polaroid frame
            padding_bottom = 80
            padding_x = padding_top = 0
        expand_rect_padding(flt_path, padding_x, padding_top, padding_bottom, flt_path)
    
    if decade == 1950:
        f = Fifties(flt_path)
    if decade == 1960:
        f = Toaster(flt_path)
    if decade == 1970:
        f = Seventies(flt_path)
    if decade == 1980:
        f = Nashville(flt_path)
    if decade == 1990:
        f = Lomo(flt_path)
    if decade == 2000:
        f = Davehill(flt_path)
 
    if f is not None:
        f.apply() # apply photo filter using imagemagick

    if decade == 1940:
        # resize fix - gotham filter output image slightly differs in size so resize it to sizes of original image
        origin_img = Image.open(path)
        width, height = origin_img.size  
        img = Image.open(flt_path)       
        img = img.resize([width,height], Image.ANTIALIAS)
        img.save(flt_path, "JPEG")

    return flt_path
