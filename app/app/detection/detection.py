#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === detection.py: script for face detection === """
import os
import uuid
import face_recognition

from PIL import Image, ImageDraw

from app.utils.utils_artface import get_largest_rect

FACE_PAD = 50 # padding for face rectangle used in image generation for age & gender prediction

def detect_faces(img_path):
    """detect faces on image, find the largest and saves images with marked face in 3 versions"""
    img_crop_path =  os.path.dirname(img_path) + "/" + str(uuid.uuid4()) + ".jpg" # path to the cropped face rectangle
    img_rect_path = os.path.dirname(img_path) + "/" + str(uuid.uuid4()) + ".jpg" # path to the image with drawn face rectangle
    img_mask_path = os.path.dirname(img_path) + "/" + str(uuid.uuid4()) + ".jpg" # path to the image with drawn face mask
    image = face_recognition.load_image_file(img_path)
    face_locations = face_recognition.face_locations(image)
    faces_num = len(face_locations)
    if faces_num < 1: # if we did not find any faces
        return ((-1, "", "", "", ""))

    selected_face = get_largest_rect(face_locations) # get face rectangle with the biggest area
    
    top, right, bottom, left = face_locations[selected_face] # get corner coordinates for selected face
    
    # cropping image to save only face rectangle with padding
    pil_image_frame = Image.fromarray(image)
    pil_image_mask = pil_image_frame.copy()
    draw_frame = ImageDraw.Draw(pil_image_frame)
    
    width = right - left
    height = bottom - top

    upper_cut = [min(pil_image_frame.size[1], top + height + FACE_PAD), min(pil_image_frame.size[0], left + width + FACE_PAD)]
    lower_cut = [max(top - FACE_PAD, 0), max(left - FACE_PAD, 0)]
    
    n_left = lower_cut[1]
    n_top = lower_cut[0]
    n_width = upper_cut[1] - lower_cut[1]
    n_height = upper_cut[0] - lower_cut[0]
    
    pil_image_crop = pil_image_frame.crop((n_left, n_top, n_left + n_width, n_top + n_height))
    pil_image_crop.save(img_crop_path, "JPEG")

    # drawing rectangle with face coordinates on image
    line_width = 5
    face_rect = (right, top, left, bottom)
    for i in range(line_width):
        draw_frame.rectangle(face_rect, outline=(0,255,0,255)) 
        face_rect = (face_rect[0] + 1,face_rect[1] + 1, face_rect[2] + 1, face_rect[3] + 1)
    pil_image_frame.save(img_rect_path, "JPEG")
    
    # drawing facial mask with face contours on image
    facial_features = [
        'chin',
        'left_eyebrow',
        'right_eyebrow',
        'nose_bridge',
        'nose_tip',
        'left_eye',
        'right_eye',
        'top_lip',
        'bottom_lip']
    draw_mask = ImageDraw.Draw(pil_image_mask)
    face_landmarks = face_recognition.face_landmarks(image)[selected_face]
    for facial_feature in facial_features:
        draw_mask.line(face_landmarks[facial_feature], width=5)
    pil_image_mask.save(img_mask_path, "JPEG")

    # calculate original image aspect ratio
    orig_image = Image.fromarray(image)
    width, height = orig_image.size
    ratio = float(height)/width

    return ((faces_num, img_crop_path, img_rect_path, img_mask_path, ratio))
    
