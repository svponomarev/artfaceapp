#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === matching.py: script for face matching with prepared database of etalon face embeddings === """

import os
import pickle
import face_recognition

from PIL import Image

from app.utils.utils_artface import get_largest_rect

def match_faces(img_path, gender):
    """match face with famous people faces searching in specific gender"""
    image_to_test = face_recognition.load_image_file(img_path)
    face_locations = face_recognition.face_locations(image_to_test)
    if len(face_locations) == 0:
        return -1

    selected_face = get_largest_rect(face_locations)  # get face rectangle with the biggest area
    output = face_recognition.face_encodings(image_to_test) # generate face encoding for current image
    
    image_to_test_encoding = output[selected_face] # get generated encoding for selected face

    with open ('app/static/db/dump_encodings', 'rb') as fp: # load encodings for famous people database
        data = pickle.load(fp)
    
    start = 0 # set search limits depending on gender
    end = 400
    if gender == "male":
        end = 200
    elif gender == "female":
        start = 200
    
    ids = data[0][start:end]
    known_encodings = data[1][start:end]
    face_distances = face_recognition.face_distance(known_encodings, image_to_test_encoding) # calculate distances between current face and faces in database
    num_of_min = 3 # get top-3 faces with minimal distance between encodings
    indices = sorted(range(len(face_distances)), key=lambda i: face_distances[i])
    top_faces = list()
    for i in indices[:num_of_min]:
        top_faces.append(tuple((ids[i], face_distances[i])))

    # calculate original image aspect ratio
    orig_image = Image.fromarray(image_to_test)
    width, height = orig_image.size
    ratio = float(height)/width
 
    # return tuples with id of people in database and calculated distance + aspect ratio
    return (top_faces, ratio) 
