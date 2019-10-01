from panda3d.core import Texture as PandaTexture
from panda3d.core import SamplerState
from panda3d.core import Vec2, Vec3, Vec4
from panda3d.core import Filename
from pathlib import Path
from direct.showbase import Loader
import sys
try:
    from PIL import Image
except:
    print(sys.exc_info())


class Texture():

    default_filtering = 'bilinear'

    def __init__(self, path):
        if 'Image' in str(type(path)):
            # print('passing pil image!')
            image = path
            self._texture = PandaTexture()
            self._texture.setup2dTexture(image.width, image.height, PandaTexture.TUnsignedByte, PandaTexture.FRgba)
            self._texture.setRamImageAs(image.transpose(Image.FLIP_TOP_BOTTOM).tobytes(), image.mode)
            self._cached_image = image.transpose(Image.FLIP_TOP_BOTTOM)
            self.path = None

        elif type(path) == PandaTexture:
            self._texture = path

        else:
            self.path = Path(path)
            self._texture = loader.loadTexture(Filename.fromOsSpecific(path))

            self._cached_image = None   # for get_pixel() method

        self.filtering = Texture.default_filtering


    @property
    def name(self):
        try:
            return self.path.name
        except:
            return f'PIL_texture_{self.size}'

    @property
    def size(self):
        return Vec2(self.width, self.height)

    @property
    def width(self):
        if self._texture.getOrigFileXSize() > 0:
            return self._texture.getOrigFileXSize()
        elif self._cached_image:
            return self._cached_image.size[0]
        return 0

    @property
    def height(self):
        if self._texture.getOrigFileYSize() > 0:
            return self._texture.getOrigFileYSize()
        elif self._cached_image:
            return self._cached_image.size[1]
        return 0

    @property
    def pixels(self):
        from numpy import asarray, flip
        from PIL import Image

        if self._cached_image:
            return asarray(self._cached_image)

        pixels = asarray(Image.open(self.path))
        pixels = flip(pixels, axis=0)
        return(pixels)


    @property
    def filtering(self):
        return self._filtering

    @filtering.setter
    def filtering(self, value):
        # print('setting filtering:', value)
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

            col = self._cached_image.getpixel((x, self.height-y-1))
            if len(col) == 3:
                return (col[0], col[1], col[2], 255)
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

    def set_pixel(self, x, y, color):
        if not self._cached_image:
            self._cached_image = Image.open(self.path)

        self._cached_image.putpixel((x, self.height-y-1), tuple([int(e*255) for e in color]))

    def apply(self):
        if not self._cached_image:
            self._cached_image = Image.open(self.path)

        self._texture.setRamImageAs(self._cached_image.transpose(Image.FLIP_TOP_BOTTOM).tobytes(), self._cached_image.mode)
        # self._texture.setRamImageAs(self._cached_image.tobytes(), self._cached_image.mode)

    def save(self, path):
        if not self._cached_image:
            self._cached_image = Image.open(self.path)

        self._cached_image.save(path)

if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    '''
        The Texture class rarely used manually but usually instantiated
        when assigning a texture to an Entity
        texture = Texture(path/PIL.Image/panda3d.core.Texture)

        A texture file can be a .png, .jpg or .psd.
        If it's a .psd it and no compressed version exists, it will compress it automatically.
    '''
    e = Entity(model='quad', texture='brick')

    for y in range(e.texture.height):
        for x in range(e.texture.width):
            if e.texture.get_pixel(x,y) == color.blue:
                print('found blue pixel at:', x, y)

    app.run()
