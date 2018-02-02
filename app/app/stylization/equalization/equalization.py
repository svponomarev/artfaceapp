#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" ===equalization.py: script for automatic color equalization of images=== """
import sys
import os
import uuid

from PIL import Image
from colorcorrect.algorithm import automatic_color_equalization
from colorcorrect.util import from_pil, to_pil

def equalize_image(img_path):
    """equalize and save output image"""
    img = Image.open(img_path)
    eq_img = to_pil(automatic_color_equalization(from_pil(img)))
    eq_path = os.path.dirname(img_path) + "/" + str(uuid.uuid4()) + ".jpg" # generate new path for equalized image in uploads folder
    eq_img.save(eq_path, "JPEG")
    return eq_path

