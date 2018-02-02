#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === utils_generate_db_dump.py: script for generating and saving face encodings of all people in database=== """
import os
import pickle
import face_recognition

from PIL import Image, ImageDraw, ImageFont

from utils_artface import get_largest_rect

def main():
    img_dir = "static/db/"
    known_encodings = []
    ids = []
    image_id = 0
    for root, dirs, files in os.walk(img_dir):
        for file in files:
            if file.endswith(".jpg"):
                print(os.path.join(root, file))
                tmp_img = face_recognition.load_image_file(os.path.join(root, file)) # detect face on current image
                tmp_locs = face_recognition.face_locations(tmp_img) # get face location
                selected_face = get_largest_rect(tmp_locs) # get number of face with largest area on image
                tmp_enc = face_recognition.face_encodings(tmp_img)[selected_face] # get encoding for selected face
                known_encodings.append(tmp_enc)
                ids.append(image_id)
                image_id = image_id + 1

    data = tuple((ids, known_encodings)) # data saved in tuples (person id, generated face encoding)

    with open('static/db/dump_encodings', 'wb') as fp: # using pickle to dump memory content into file on disk
        pickle.dump(data, fp)

if __name__ == "__main__":
    main()
