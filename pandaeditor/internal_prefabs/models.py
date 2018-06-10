from pandaeditor import *

class Quad(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'quad'
        # super().__init__(**kwargs)
# def Quad(self, **kwargs):
#     e = Entity()

class Circle(Entity):
    def __init__(self, resolution=16):
        super().__init__()
        self.model = circle(resolution)

class Cube(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'cube'

def circle(resolution=16, radius=.5):
    origin = Entity()
    point = Entity(parent=origin)
    point.y = radius

    verts = list()
    for i in range(resolution):
        origin.rotation_z -= 360 / resolution
        print(point.world_position)
        verts.append(point.world_position)

    destroy(origin)

    return Mesh(verts, mode='ngon')

if __name__ == '__main__':
    app = PandaEditor()
    c = Circle()
    # e = Entity()
    # e.model = circle()
    # e.model = 'circle_16'
    # print('----', e.model)
    # # e.rotation_y = 90
    app.run()
