#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" based on https://gist.github.com/motiondesignstudio/9374326"""
import sys
import os
import PIL

from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from PIL import ImageOps

import aalib

img_new_magnitude=5
fontsize= 14
font_color = (0,200,0)
background_color = (0,0,0)
font = ImageFont.truetype(os.path.dirname(os.path.realpath(__file__)) + "/fonts/FreeMonoBold.ttf", fontsize, encoding="unic")

def create_ascii_image(img_path, out_path):
    """generate ascii image using aalib and exports it to jpeg file"""
    myimage= Image.open(img_path)
    image_width, image_height = myimage.size

    aalib_screen_width= int(image_width/24.9)*img_new_magnitude
    aalib_screen_height= int(image_height/41.39)*img_new_magnitude

    screen = aalib.AsciiScreen(width=aalib_screen_width, height=aalib_screen_height )

    myimage= Image.open(img_path).convert("L").resize(screen.virtual_size)

   
    screen.put_image((0,0), myimage)

    y = 0

    how_many_rows = len ( screen.render().splitlines() )

    new_img_width, font_size = font.getsize (screen.render().splitlines()[0])

    img=Image.new("RGB", (new_img_width, how_many_rows*fontsize), background_color)

    draw = ImageDraw.Draw(img)
    
    for lines in screen.render().splitlines():
        draw.text( (0,y), lines, font_color,font=font )
        y = y + fontsize
    
    imagefit = ImageOps.fit(img, (image_width, image_height), Image.ANTIALIAS)
    imagefit.save(out_path, "JPEG")

def main():
    img_path = "input.jpg"
    out_path = "output.jpg"
    create_ascii_image(img_path, out_path)

if __name__ == '__main__':
    main()
