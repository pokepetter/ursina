from ursina import *
from PIL import Image


class Terrain(Plane):
    def __init__(self, heightmap, skip=1, **kwargs):
        self.heightmap = load_texture(heightmap)

        image = Image.open(self.heightmap.path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        w, h = self.heightmap.width, self.heightmap.height
        image = image.resize([w//skip, h//skip], Image.ANTIALIAS)
        self.heightmap = Texture(image)
        w, h = self.heightmap.width, self.heightmap.height

        super().__init__(subdivisions=(w-1, h-1), **kwargs)
        i = 0
        for y in range(h):
            for x in range(w):
                h = self.heightmap.get_pixel(x, y).v
                self.vertices[i] = (self.vertices[i][0], h, self.vertices[i][2])
                i += 1

        self.generate()




if __name__ == '__main__':
    app = Ursina()
    e = Entity(model=Terrain('heightmap_1', skip=2), scale=5)
    # e.model.colorize()
    e.texture='heightmap_1'
    EditorCamera()

    app.run()
