from ursina import *


class Grid(Mesh):
    def __init__(self, width, height, thickness=1, **kwargs):
        self.width = width
        self.height = height

        verts = list()
        for x in range(int(width) + 1):
            verts.append((x/width, 0, 0))
            verts.append((x/width, 1, 0))
        for y in range(int(height) + 1):
            verts.append((0, y/height, 0))
            verts.append((1, y/height, 0))

        super().__init__(verts, mode='line', **kwargs)



if __name__ == '__main__':
    app = Ursina()
    Entity(model=Grid(2, 6))
    app.run()
