#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === utils_rescale_db.py: script for resizing all of the images in faces database keeping the aspect ratio === """

import os
import pickle
import face_recognition

from PIL import Image, ImageDraw, ImageFont

def main():
    img_dir = "static/db/"
    size = (400, 400)
    for root, dirs, files in os.walk(img_dir):
        for file in files:
            if file.endswith(".jpg"):
                impath = os.path.join(root, file)
                print(impath)
                im = Image.open(impath)
                width, height = im.size
                if width > 400:
                    im.thumbnail(size, Image.ANTIALIAS)
                    im.save(impath, "JPEG")

if __name__ == '__main__':
    main()
