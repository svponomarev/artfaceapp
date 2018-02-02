#!/usr/bin/python
# -*- coding: utf-8 -*-
"""see also https://github.com/mosesschwartz/warhol_effect"""
import sys

from PIL import Image

colorset = [
    {'bg': (255, 255, 0, 255), 'fg': (50, 9, 125, 255), 'skin': (118,
     192, 0, 255)},
    {'bg': (0, 122, 240, 255), 'fg': (255, 0, 112, 255), 'skin': (255,
     255, 0, 255)},
    {'bg': (50, 0, 130, 255), 'fg': (255, 0, 0, 255), 'skin': (243,
     145, 192, 255)},
    {'bg': (255, 126, 0, 255), 'fg': (134, 48, 149, 255), 'skin': (111,
     185, 248, 255)},
    {'bg': (255, 0, 0, 255), 'fg': (35, 35, 35, 255), 'skin': (255,
     255, 255, 255)},
    {'bg': (122, 192, 0, 255), 'fg': (255, 89, 0, 255), 'skin': (250,
     255, 160, 255)},
    {'bg': (0, 114, 100, 255), 'fg': (252, 0, 116, 255), 'skin': (250,
     250, 230, 255)},
    {'bg': (250, 255, 0, 255), 'fg': (254, 0, 0, 255), 'skin': (139,
     198, 46, 255)},
    {'bg': (253, 0, 118, 255), 'fg': (51, 2, 126, 255), 'skin': (255,
     105, 0, 255)},
    ]

fg_temp = 0
skin_temp = 128
bg_temp = 255


def getLUT(h):

    # return [fg_temp if i < 128 else bg_temp for i in range(256)]

    lut = []
    for i in range(256):
        if i < 86:
            lut.append(fg_temp)
        elif 86 < i < 172:
            lut.append(skin_temp)
        else:
            lut.append(bg_temp)
    return lut


def getHistogram(image):
    '''Ritorno un istogramma dei colori'''

    histogram = {}
    pixdata = image.convert('L').load()
    for y in xrange(image.size[1]):
        for x in xrange(image.size[0]):
            c = pixdata[x, y]
            histogram[c] = histogram.get(c, 0) + 1
    return histogram


class OriginalImage(object):

    def __init__(self, fname):
        self.image = Image.open(fname)
        h = getHistogram(self.image)
        self.lut = getLUT(h)

    def bw(self):
        '''I colori pi\xf9 chiari (idealmento lo sfondo) dovrebbero essere trasformati in bianco'''

        self.image = self.image.convert('L')
        self.image = self.image.point(self.lut)
        self.image = self.image.convert('RGBA')

    def setFgColor(
        self,
        warhols,
        x,
        y,
        ):

        for (i, colors) in enumerate(colorset):
            pixdata = warhols[i]
            pixdata[x, y] = colors['fg']

    def setSkinColor(
        self,
        warhols,
        x,
        y,
        ):

        for (i, colors) in enumerate(colorset):
            pixdata = warhols[i]
            pixdata[x, y] = colors['skin']

    def setBgColor(
        self,
        warhols,
        x,
        y,
        ):

        ret = []
        for (i, colors) in enumerate(colorset):
            pixdata = warhols[i]
            pixdata[x, y] = colors['bg']

    def make_warhol(self, warhols):
        '''create a single warhol-serigraph-style image'''

        pixdata = self.image.load()
        for y in xrange(self.image.size[1]):
            for x in xrange(self.image.size[0]):
                if pixdata[x, y] == (fg_temp, fg_temp, fg_temp, 255):
                    self.setFgColor(warhols, x, y)
                if pixdata[x, y] == (skin_temp, skin_temp, skin_temp,
                        255):
                    self.setSkinColor(warhols, x, y)
                if pixdata[x, y] == (bg_temp, bg_temp, bg_temp, 255):
                    self.setBgColor(warhols, x, y)

    def warholify(self):
        self.bw()

        warhols = []
        warholsLoads = []
        for colors in colorset:
            im = self.image.copy().convert('RGBA')
            warhols.append(im)
            warholsLoads.append(im.load())

        self.make_warhol(warholsLoads)

        x = self.image.size[0]
        y = self.image.size[1]

        self.image = Image.new('RGB', (x * 3, y * 2))
        self.image.paste(warhols[0], (0, 0))
        self.image.paste(warhols[1], (x, 0))
        self.image.paste(warhols[2], (x * 2, 0))
        self.image.paste(warhols[3], (0, y))
        self.image.paste(warhols[4], (x, y))
        self.image.paste(warhols[5], (x * 2, y))

    def save(self, fname):
        self.image.save(fname)


if __name__ == '__main__':
    try:
        fname = sys.argv[1]
        i = OriginalImage(sys.argv[1])
        i.warholify()
        i.save('out.png')
    except IndexError:
        print 'Usage: python main.py <file>'
