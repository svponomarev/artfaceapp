#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === utils_artface.py: script for various reusable functions === """

def get_largest_rect(rects):
    """returns rectangle with the biggest area"""
    selected_rect = 0
    max_area = 0
    for i in range(len(rects)):
        top, right, bottom, left = rects[i]
        height = bottom - top
        width = right - left
        area = height * width
        if area > max_area:
            selected_rect = i
            max_area = area
    return selected_rect
