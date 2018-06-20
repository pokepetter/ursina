from ursina import *


class Grid(Entity):
    def __init__(self, w, h, thickness=1, **kwargs):
        super().__init__(**kwargs)

        verts = list()
        for x in range(int(w) + 1):
            verts.append((x/w, 0, 0))
            verts.append((x/w, 1, 0))
        for y in range(int(h) + 1):
            verts.append((0, y/h, 0))
            verts.append((1, y/h, 0))

        if 'color' in kwargs:
            self.model = Mesh(verts, colors=[kwargs['color'] for v in verts], mode='line', thickness=thickness)
        else:
            self.model = Mesh(verts, mode='line', thickness=thickness)

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        self._thickness = value
        self.model.thickness = value
