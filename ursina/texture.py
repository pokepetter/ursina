from panda3d.core import Texture as PandaTexture
# print('unsigned byte', PandaTexture.TUnsignedByte)
from panda3d.core import SamplerState
from panda3d.core import Vec2, Vec3, Vec4
from panda3d.core import Filename
from pathlib import Path
from direct.showbase import Loader
from PIL import Image


class Texture():

    def __init__(self, path=''):
        if path == '':
            self._texture = PandaTexture()
        else:
            self.path = Path(path)
            self._texture = loader.loadTexture(Filename.fromOsSpecific(path))

        self.filtering = None
        self._cached_image = None   # for get_pixel() method


    @property
    def name(self):
        return self.path.name

    @property
    def size(self):
        return Vec2(self.width, self.height)

    @property
    def width(self):
        try:
            return self._texture.getOrigFileXSize()
        except:
            return 0
    @property
    def height(self):
        try:
            return self._texture.getOrigFileYSize()
        except:
            return 0

    @property
    def pixels(self):
        from numpy import asarray
        return asarray(Image.open(self.path))

    @property
    def filtering(self):
        return self._filtering

    @filtering.setter
    def filtering(self, value):
        if value in (None, False, 'nearest', 'nearest neighbor'):
            self._texture.setMagfilter(SamplerState.FT_nearest)
            self._texture.setMinfilter(SamplerState.FT_nearest)
            self._filtering = False
        elif value in (True, 'linear', 'bilinear'):
            self._texture.setMagfilter(SamplerState.FT_linear)
            self._texture.setMinfilter(SamplerState.FT_linear)
            self._filtering = True


    def get_pixel(self, x, y):
        try:
            if not self._cached_image:
                self._cached_image = Image.open(self.path)

            col = self._cached_image.getpixel((x, self.height - y -1))
            if len(col) == 3:
                return (col[0], col[1], col[2], 1)
            else:
                return (col[0], col[1], col[2], col[3])
        except:
            return None


    def get_pixels(self, start, end):
        start = (clamp(start[0], 0, self.width), clamp(start[1], 0, self.width))
        end = (clamp(end[0], 0, self.width), clamp(end[1], 0, self.width))
        pixels = list()

        for y in range(start[1], end[1]):
            for x in range(start[0], end[0]):
                pixels.append(self.get_pixel(x,y))

        return pixels


if __name__ == '__main__':
    from ursina import *
    Ursina()
    t = load_texture('brick')
    print(t.size)
    printvar(t.filtering)
    printvar(t.name)
    printvar(t.path)
    printvar(len(t.pixels))
