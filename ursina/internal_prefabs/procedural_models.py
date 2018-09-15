from ursina import *



class Circle(Entity):
    def __init__(self, resolution=16):
        super().__init__()
        self.model = circle(resolution)

class Cube(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'cube'

class Circle(Mesh):
    def __init__(self, resolution=16, radius=.5, **kwargs):
        origin = Entity()
        point = Entity(parent=origin)
        point.y = radius

        self.verts = list()
        for i in range(resolution):
            origin.rotation_z -= 360 / resolution
            verts.append(point.world_position)

        destroy(origin)
        super().__init__(verts=self.verts, mode='ngon', **kwargs)


class Quad(Mesh):
    def __init__(self, size=(1,1), bevel=.1, subdivisions=0, ignore_aspect=False, **kwargs):
        self.verts = (Vec3(0,0,0), Vec3(1,0,0), Vec3(1,1,0), Vec3(0,1,0))

        for j in range(subdivisions):
            points = list()
            for i, v in enumerate(self.verts):
                points.append(lerp(v, self.verts[i-1], bevel))
                next_index = i+1 if i+1 < len(self.verts) else 0
                points.append(lerp(v, self.verts[next_index], bevel))
            self.verts = points

        uvs = list()
        for v in self.verts:
            uvs.append((v[0], v[1]))

        # move edges out like a 9 slice
        for v in self.verts:
            if v[0] <= (1/3):
                v[0] -= (size[0] - 1) / 4
            if v[0] >= (2/3):
                v[0] += (size[0] - 1) / 4

            if v[1] <= (1/3):
                v[1] -= (size[1] - 1) / 4
            if v[1] >= (2/3):
                v[1] += (size[1] - 1) / 4


        # make the line connect back to start
        if 'mode' in kwargs and kwargs['mode'] == 'lines':
            self.verts.append(self.verts[0])

        # center mesh
        offset = average_position(self.verts)
        self.verts = [(v[0]-offset[0], v[1]-offset[1], v[2]-offset[2]) for v in self.verts]

        super().__init__(verts=self.verts, uvs=uvs, **kwargs)



class Sphere(Mesh):
    def __init__(self, radius=.5, subdivision=0, **kwargs):
        # Make the base icosahedron
        # Golden ratio
        PHI = (1 + sqrt(5)) / 2

        verts = [(-1,  PHI, 0), ( 1,  PHI, 0), (-1, -PHI, 0), ( 1, -PHI, 0),
                 (0, -1, PHI), (0,  1, PHI), (0, -1, -PHI), (0,  1, -PHI),
                 ( PHI, 0, -1), ( PHI, 0,  1), (-PHI, 0, -1), (-PHI, 0,  1),
                ]

        faces = [
            [0, 11, 5],[0, 5, 1],[0, 1, 7],[0, 7, 10],[0, 10, 11],# 5 faces around point 0
            [1, 5, 9],[5, 11, 4],[11, 10, 2],[10, 7, 6],[7, 1, 8],# Adjacent faces
            [3, 9, 4],[3, 4, 2],[3, 2, 6],[3, 6, 8],[3, 8, 9],# 5 faces around 3
            [4, 9, 5],[2, 4, 11],[6, 2, 10],[8, 6, 7],[9, 8, 1],# Adjacent faces
            ]

        super().__init__(verts=verts, mode='point', thickness=16, **kwargs)




if __name__ == '__main__':
    app = Ursina()

    e = Entity(
        # scale_x = 3,
        # model = Quad(size=(3,1), subdivisions=2, thickness=3, mode='lines'),
        model = Sphere(),
        # texture = 'brick',
        texture_scale = (2,1),
        color = color.yellow
        )
    e.scale *= 2

    Entity(model='quad', color=color.orange, scale=(.05, .05))
    EditorCamera()

    # quad.scale_x = 3
    # e = Entity()
    # e.model = circle()
    # e.model = 'circle_16'
    # print('----', e.model)
    # # e.rotation_y = 90
    app.run()
