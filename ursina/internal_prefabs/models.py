from ursina import *

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


class Quad(Mesh):
    def __init__(self, bevel=.1, subdivisions=0, ignore_aspect=False, **kwargs):
        if subdivisions == 0:
            super().__init__(verts=None)
            self = Entity(model='quad').model
        else:
            self.verts = (Vec3(-.5,-.5,0), Vec3(.5,-.5,0), Vec3(.5,.5,0), Vec3(-.5,.5,0))

            for j in range(subdivisions):
                points = list()
                for i, v in enumerate(self.verts):
                    points.append(lerp(v, self.verts[i-1], bevel))
                    next_index = i+1 if i+1 < len(self.verts) else 0
                    points.append(lerp(v, self.verts[next_index], bevel))
                self.verts = points

            uvs = list()
            for v in self.verts:
                uvs.append((v[0] + .5, v[1] + .5))

            # printvar(uvs)
            # if not ignore_aspect and self.parent:
            # print('..................', )
            aspect_x = 3
            for v in self.verts:
                if v[0] < 0:
                    v[0] = lerp(v[0], -.5, 1 / aspect_x)


            # mode = 'ngon'
            # if 'mode' in kwargs:
            #     print('yolo')
            #     mode = kwargs['mode']

            super().__init__(verts=self.verts, uvs=uvs, **kwargs)

    def on_assign(self, assigned_to):
        print('assign model', self.__class__.__name__, 'to:', assigned_to)
        verts = self.verts
        


if __name__ == '__main__':
    app = Ursina()

    e = Entity(
        scale_x = 3,
        model = Quad(subdivisions=2, thickness=10),
        texture = 'brick',
        texture_scale = (2,1),
        color = color.yellow
        )
    e.scale *= 2


    # quad.scale_x = 3
    # e = Entity()
    # e.model = circle()
    # e.model = 'circle_16'
    # print('----', e.model)
    # # e.rotation_y = 90
    app.run()
