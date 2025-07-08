from panda3d.core import Texture as PandaTexture
from panda3d.core import TexturePool
from panda3d.core import SamplerState
from panda3d.core import Filename
from panda3d.core import PNMImage
from pathlib import Path
from ursina.vec2 import Vec2
from ursina import color
from ursina.ursinamath import clamp
from ursina.array_tools import Array2D, enumerate_2d
from ursina.scripts.property_generator import generate_properties_for_class

@generate_properties_for_class()
class Texture():

    default_filtering = None      # options: None / 'bilinear' / 'mipmap'

    def __init__(self, value, filtering='default'):

        if isinstance(value, str) and value.startswith('data:image/png;base64'):
            import base64
            from PIL import Image
            from io import BytesIO
            base64_data = value.lstrip('data:image/png;base64')   # remove prefix
            value = Image.open(BytesIO(base64.b64decode(base64_data))).convert('RGBA')

        elif isinstance(value, str):
            value = Path(value)

        if isinstance(value, Path):
            self.path = Path(value)
            self._texture = TexturePool.loadTexture(Filename.fromOsSpecific(str(value)))
            self._cached_image = None   # for get_pixel() method

        elif isinstance(value, PandaTexture):
            self._texture = value

        else:
            from PIL import Image
            image = value.convert('RGBA')
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


    def name_getter(self):
        try:
            return self.path.name
        except:
            return f'PIL_texture_{self.size}'


    def __str__(self):
        return self.name


    def size_getter(self):
        return Vec2(self.width, self.height)

    def width_getter(self):
        if self._cached_image:
            return self._cached_image.size[0]
        elif self._texture.getOrigFileXSize() > 0:
            return self._texture.getOrigFileXSize()
        return 0

    def height_getter(self):
        if self._cached_image:
            return self._cached_image.size[1]
        elif self._texture.getOrigFileYSize() > 0:
            return self._texture.getOrigFileYSize()
        return 0


    def pixels_getter(self):
        pixels = Array2D(*self.size, default_value=None)
        for (x,y), value in enumerate_2d(pixels):
            pixels[x][y] = self.get_pixel(x, y)

        return pixels

    def filtering_setter(self, value):
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


    def repeat_setter(self, value):
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


    def to_PIL_Image(self):
        from PIL import Image
        # Ensure the texture data is available
        # self._texture.prepareRamImage()

        # Get the size and format
        width = self._texture.getXSize()
        height = self._texture.getYSize()

        # Get the raw image data as bytes in RGB format
        data = self._texture.getRamImageAs("RGB")
        if data is None:
            raise RuntimeError("Texture has no RAM image data")

        # Convert from bottom-up to top-down image
        image = Image.frombytes("RGB", (width, height), data.getData())
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        return image


    def __repr__(self):
        return self.name


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
    e = Entity(model='quad', texture='test_tileset')
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

    e.texture = 'test_tileset'
    # e.texture.set_pixels([e for e in e.texture.get_pixels()])
    e.texture.apply()

    # tex = Texture.new((512,512), (255,0,0))

    pixels = e.texture.pixels
    new_grid = Array2D(width=pixels.width, height=pixels.height)
    print('w:', pixels.width, 'h:', pixels.height)
    for (x,y), value in enumerate_2d(pixels):
        new_grid[x][y] = int(color.rgba32(*value).v > .5)


    texture_from_base64_string = Entity(model='cube', y=1.5, scale=1, texture=Texture('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAQAAAAECAIAAAAmkwkpAAAAJ0lEQVR4nGK5d/gdAwODArcEkGRiQAKMmut0gdTX/YroMoAAAAD//8caBbV8Qu6pAAAAAElFTkSuQmCC'))
    EditorCamera()

    # print(new_grid)
    app.run()
