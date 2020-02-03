from ursina import *


class Terrain(Plane):
    def __init__(self, heightmap, skip=1, **kwargs):
        self.heightmap = load_texture(heightmap)
        if not self.heightmap:
            print('failed to load heightmap:', heightmap)
            return

        w, d = self.heightmap.width//skip, self.heightmap.height//skip
        if skip > 1:
            from PIL import Image
            img = Image.open(self.heightmap.path)
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            img = img.resize([w, d], Image.ANTIALIAS)
            self.heightmap = Texture(img)

        super().__init__(subdivisions=(w, d), **kwargs)

        i = 0
        for z in range(d+1):
            for x in range(w+1):

                if x < w and z < d:
                    y = self.heightmap.get_pixel(x, z).r
                self.vertices[i] = Vec3(x/w -.5, y, z/d -.5)
                i += 1

        self.generate()




if __name__ == '__main__':
    app = Ursina()
    e = Entity(model=Terrain('heightmap_1', skip=8), scale=5)
    e.texture='heightmap_1'
    Entity(model=Plane(), scale=5, color=color.blue)
    EditorCamera()

    app.run()
