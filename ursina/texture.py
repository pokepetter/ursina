from panda3d.core import Texture as PandaTexture
from panda3d.core import SamplerState
from panda3d.core import Filename
from panda3d.core import PNMImage
from pathlib import Path
from ursina.vec2 import Vec2
from ursina import color
from ursina.ursinamath import clamp


class Texture():

    default_filtering = None      # options: None / 'bilinear' / 'mipmap'

    def __init__(self, value, filtering='default'):

        if isinstance(value, str):
            value = Path(value)

        if isinstance(value, Path):
            self.path = Path(value)
            self._texture = loader.loadTexture(Filename.fromOsSpecific(str(value)))
            self._cached_image = None   # for get_pixel() method

        elif isinstance(value, PandaTexture):
            self._texture = value

        else:
            from PIL import Image
            image = value
            self._texture = PandaTexture()
            self._texture.setup2dTexture(image.width, image.height, PandaTexture.TUnsignedByte, PandaTexture.FRgba)
            self._texture.setRamImageAs(image.transpose(Image.FLIP_TOP_BOTTOM).tobytes(), image.mode)
            self._cached_image = image   # for get_pixel() method
            # self._cached_image = image.transpose(Image.FLIP_TOP_BOTTOM)
            self.path = None

        if filtering == 'default':
            filtering = Texture.default_filtering      # None/'bilinear'/'mipmap' default: 'None'
        self.filtering = filtering


    @staticmethod
    def new(size, color=(255,255,255)):
        img = PNMImage(*size)
        if len(color) == 4:
            img.addAlpha()

        img.fill(*color)
        panda_tex = PandaTexture('texture')
        panda_tex.load(img)
        return Texture(panda_tex)


    @property
    def name(self):
        try:
            return self.path.name
        except:
            return f'PIL_texture_{self.size}'

    def __str__(self):
        return self.name


    @property
    def size(self):
        return Vec2(self.width, self.height)

    @property
    def width(self):
        if self._cached_image:
            return self._cached_image.size[0]
        elif self._texture.getOrigFileXSize() > 0:
            return self._texture.getOrigFileXSize()
        return 0

    @property
    def height(self):
        if self._cached_image:
            return self._cached_image.size[1]
        elif self._texture.getOrigFileYSize() > 0:
            return self._texture.getOrigFileYSize()
        return 0

    @property
    def pixels(self):
        from numpy import asarray, flip
        from PIL import Image

        if self._cached_image:
            return asarray(self._cached_image)

        pixels = asarray(Image.open(self.path))
        pixels = flip(pixels, axis=0)
        return pixels


    @property
    def filtering(self):
        return self._filtering

    @filtering.setter
    def filtering(self, value):
        # print('setting filtering:', value)
        if value in (None, False, 'nearest', 'nearest neighbor', 'point'):
            self._texture.setMagfilter(SamplerState.FT_nearest)
            self._texture.setMinfilter(SamplerState.FT_nearest)
            self._filtering = False
        elif value in (True, 'linear', 'bilinear'):
            self._texture.setMagfilter(SamplerState.FT_linear)
            self._texture.setMinfilter(SamplerState.FT_linear)
            self._filtering = True
        elif value == 'mipmap':
            self._texture.setMinfilter(SamplerState.FT_linear_mipmap_linear)
            self._filtering = 'mipmap'

    @property
    def repeat(self):
        return self._repeat

    @repeat.setter
    def repeat(self, value):
        self._repeat = value
        self._texture.setWrapU(value)
        self._texture.setWrapV(value)


    def get_pixel(self, x, y):
        try:
            if not self._cached_image:
                from PIL import Image
                self._cached_image = Image.open(self.path)


            col = self._cached_image.getpixel((x, self.height-y-1))
            if self._cached_image.mode == 'LA':
                col = (col[0], col[0], col[0], col[1])

            if self._cached_image.mode == 'L':
                col = (col[0], col[0], col[0])

            return color.rgba32(*col)
        except Exception as e:
            print(e)
            return None


    def get_pixels(self, start, end):
        start = (clamp(start[0], 0, self.width), clamp(start[1], 0, self.width))
        end = (clamp(end[0], 0, self.width), clamp(end[1], 0, self.width))
        pixels = []

        for y in range(start[1], end[1]):
            for x in range(start[0], end[0]):
                pixels.append(self.get_pixel(x,y))

        return pixels

    def set_pixel(self, x, y, color):
        if not self._cached_image:
            from PIL import Image
            self._cached_image = Image.open(self.path)

        self._cached_image.putpixel((x, self.height-y-1), tuple(int(e*255) for e in color))

    def apply(self):
        from PIL import Image
        if not self._cached_image:
            self._cached_image = Image.open(self.path)

        self._texture.setRamImageAs(self._cached_image.transpose(Image.FLIP_TOP_BOTTOM).tobytes(), self._cached_image.mode)
        # self._texture.setRamImageAs(self._cached_image.tobytes(), self._cached_image.mode)

    def save(self, path):
        if not self._cached_image:
            from PIL import Image
            self._cached_image = Image.open(self.path)

        self._cached_image.save(path)

    def __repr__(self):
        return self.name


    def __del__(self):
        # self._texture.releaseAll()
        del self._cached_image



if __name__ == '__main__':
    from ursina import *
    from ursina import texture_importer
    app = Ursina()
    '''
        The Texture class rarely used manually but usually instantiated
        when assigning a texture to an Entity
        texture = Texture(path / PIL.Image / panda3d.core.Texture)

        A texture file can be a .png, .jpg or .psd.
        If it's a .psd it and no compressed version exists, it will compress it automatically.
    '''
    e = Entity(model='quad', texture='brick')
    e.texture.set_pixel(0, 2, color.blue)
    e.texture.apply()
    #
    # for y in range(e.texture.height):
    #     for x in range(e.texture.width):
    #         if e.texture.get_pixel(x,y) == color.blue:
    #             print('found blue pixel at:', x, y)

    # test
    application.asset_folder = Path(r'C:\sync\high resolution images')
    e = Entity(model='quad')
    # from PIL import Image

    # from ursina.prefabs.memory_counter import MemoryCounter
    # MemoryCounter()
    def input(key):
        if key == 'a':
            # img = Image.open(r'C:\sync\high resolution images\tesla_city.png')
            # print('-------', img)
            # e.texture = Texture(img)
            e.texture = 'tesla_city'

        if key == 'space':
            # if not 'tesla_city' in texture_importer.imported_textures:
            #     return
            # print('del texture')
            # del texture_importer.imported_textures['tesla_city']
            # del e.texture
            # tex = e.texture._texture
            t = e.texture._texture
            # e.texture._texture = None
            e.texture = None
            t.releaseAll()
            # print(t.releaseAll())
            t.clearRamImage()
            # e.texture._texture.clear()
            # e.texture._texture = None
            # e.texture = None
            # destroy(e)
        if key == 'p':
            for key, value in texture_importer.imported_textures.items():
                print(key, value)

    e.texture = 'brick'
    # e.texture.set_pixels([e for e in e.texture.get_pixels()])
    e.texture.apply()
    tex = Texture.new((512,512), (255,0,0))

    app.run()
