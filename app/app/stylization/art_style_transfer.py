#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === art_style_transfer.py: script for applying art style transfer on image using neural networks and other techniques === """
import os
import shutil
import uuid
import requests
import base64
import face_recognition
import json
import csv
import cStringIO

from PIL import Image

from art_style.warholify import OriginalImage
from art_style.asciinator import create_ascii_image
from app.utils.utils_artface import get_largest_rect

def crop_face_rect(img_path, rect, FACE_PAD, out_path):
    """crops image using coordinates of face rectangle and selected padding"""
    top, right, bottom, left = rect
    
    pil_image_frame = Image.open(img_path)
    
    width = right - left
    height = bottom - top

    upper_cut = [min(pil_image_frame.size[1], top + height + FACE_PAD), min(pil_image_frame.size[0], left + width + FACE_PAD)]
    lower_cut = [max(top - FACE_PAD, 0), max(left - FACE_PAD, 0)]
    
    n_left = lower_cut[1]
    n_top = lower_cut[0]
    n_width = upper_cut[1] - lower_cut[1]
    n_height = upper_cut[0] - lower_cut[0]
    
    pil_image_crop = pil_image_frame.crop((n_left, n_top, n_left + n_width, n_top + n_height))
    pil_image_crop.save(out_path, "JPEG")

def get_styles_names(decade):
    """loads names of art styles from csv file for selected decade"""
    csv_db = os.path.dirname(os.path.realpath(__file__)) + '/art_style/decade_styles.csv'
    style1 = style2 = style3 = ""
    with open(csv_db, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader) # skip row with column names
        for row in reader:
            cur_decade = int(row[0])
            style1 = row[1]
            style2 = row[2]
            style3 = row[3]
            if cur_decade == decade:
                break
    return (style1, style2, style3)


def apply_art_style(orig_path, eql_path, decade, style_num):
    """stylize image with specific art style according to selected decade and style number"""
    trs_path = os.path.dirname(eql_path) + "/" + str(uuid.uuid4()) + ".jpg"
    style1, style2, style3 = get_styles_names(decade)
    if not 0 <= style_num <= 2: # check that style_num has valid value
        style_num = 0 # otherwise choose first style by default
    if decade == 1960 and style_num == 2: # apply warhol style in 1960s using separate python script
        image = face_recognition.load_image_file(orig_path)
        # face detection is applied to extract only face rectangle for style transfer
        face_locations = face_recognition.face_locations(image)
        faces_num = len(face_locations)
        if faces_num >= 1:
            selected_face = get_largest_rect(face_locations)
            FACE_PAD = 50
            crop_face_rect(orig_path, face_locations[selected_face], FACE_PAD, trs_path)
            img = OriginalImage(trs_path) # apply warhol filter on face rectangle
        else:
            img = OriginalImage(orig_path) # apply warhol filter on whole image
        img.warholify()
        img.save(trs_path)
    elif decade == 1990 and style_num == 2: # apply ascii image generation in 1990s using separate python script
        create_ascii_image(eql_path, trs_path)
    else: # using magenta arbitrary style transfer in all other cases
        style_path = "app/static/images/styles/" + str(decade) + "/" + str(style_num) + ".jpg" # generate path to image with selected style

        content_img = ""
        style_img = ""

        # read content and style image in base64 encoding
        with open(eql_path, "rb") as image_file:
            content_img = base64.b64encode(image_file.read()) 

        with open(style_path, "rb") as image_file:
            style_img = base64.b64encode(image_file.read())

        # prepare json data for post request
        dataToSend = {'content_img':content_img, 'style_img': style_img}
        
        res = requests.post('http://172.18.0.13:6006/', json=dataToSend) # send request to dedicated Flask server with running magenta neural net
        
        dataDict = res.json() # get output from neural network in form of base64 encoded stylized image
        
        decoded_img = base64.decodestring(dataDict['out_img']) #decode base64 string

        # resize fix - neural net output image slightly differs in size so resize it to sizes of original image
        origin_img = Image.open(eql_path)
        width, height = origin_img.size  
        file_like = cStringIO.StringIO(decoded_img)
        img = Image.open(file_like)       
        img = img.resize([width,height], Image.ANTIALIAS)
        img.save(trs_path, "JPEG")

        # print 'Time to process:',dataDict['Processing time']
                 

    return (trs_path, style1, style2, style3) # returns path to the stylized image and names of styles for selected decade
