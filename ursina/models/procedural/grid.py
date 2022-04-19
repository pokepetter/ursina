from ursina import *


class Grid(Mesh):
    def __init__(self, width, height, mode='line', thickness=1, **kwargs):
        self.width = width
        self.height = height

        verts = list()
        tris = list()

        for x in range(int(width) + 1):
            verts.append(Vec3(-.5 + (x/width), -.5, 0))
            verts.append(Vec3(-.5 + (x/width), .5, 0))

        for y in range(int(height) + 1):
            verts.append((-.5, -.5 + (y/height), 0))
            verts.append((.5, -.5 + (y/height), 0))

        tris = [(i, i+1) for i in range(0, len(verts), 2)]

        super().__init__(verts, triangles=tris, mode=mode, thickness=thickness, **kwargs)



if __name__ == '__main__':
    app = Ursina()
    Entity(model=Grid(2, 6))
    app.run()
