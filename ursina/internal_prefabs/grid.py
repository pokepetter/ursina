from ursina import *


class Grid(Mesh):
    def __init__(self, w, h, thickness=1, **kwargs):

        verts = list()
        for x in range(int(w) + 1):
            verts.append((x/w, 0, 0))
            verts.append((x/w, 1, 0))
        for y in range(int(h) + 1):
            verts.append((0, y/h, 0))
            verts.append((1, y/h, 0))

        super().__init__(verts, mode='line', **kwargs)



if __name__ == '__main__':
    app = Ursina()
    Entity(model=Grid(2, 6))
    app.run()
