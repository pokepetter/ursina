from panda3d.core import Texture as PandaTexture
from panda3d.core import Vec2, Vec3, Vec4
from PIL import Image


class Texture(PandaTexture):

    @property
    def name(self):
        return self.getFilename()

    @property
    def path(self):
        return Path(self.getFullpath().toOsSpecific())

    @property
    def size(self):
        return Vec2(self.width, self.height)

    @property
    def width(self):
        try:
            return self.getOrigFileXSize()
        except:
            return 0
    @property
    def height(self):
        try:
            return self.getOrigFileYSize()
        except:
            return 0

    @property
    def pixels(self):
        from numpy import asarray
        return asarray(Image.open(self.texture_path))


    def get_pixel(self, x, y):
        try:
            if not self._cached_image:
                self._cached_image = Image.open(self.texture_path)

            col = self._cached_image.getpixel((x, self.texture_height - y -1))
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
