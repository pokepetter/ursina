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

        verts = list()
        for i in range(resolution):
            origin.rotation_z -= 360 / resolution
            verts.append(point.world_position)

        destroy(origin)
        super().__init__(verts=verts, mode='ngon', **kwargs)


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
        # PHI = (1 + sqrt(5)) / 2
        #
        # verts = [(-1,  PHI, 0), ( 1,  PHI, 0), (-1, -PHI, 0), ( 1, -PHI, 0),
        #          (0, -1, PHI), (0,  1, PHI), (0, -1, -PHI), (0,  1, -PHI),
        #          (PHI, 0, -1), (PHI, 0,  1), (-PHI, 0, -1), (-PHI, 0,  1),
        #         ]
        #
        # faces = (
        #     0,11,5, 0,5,1,  0,1,7,   0,7,10, 0,10,11,   # 5 faces around point 0
        #     1,5,9,  5,11,4, 11,10,2, 10,7,6, 7,1,8,     # Adjacent faces
        #     3,9,4,  3,4,2,  3,2,6,   3,6,8,  3,8,9,     # 5 faces around 3
        #     4,9,5,  2,4,11, 6,2,10,  8,6,7,  9,8,1      # Adjacent faces
        #     )
        X=.525731112119133606
        Z=.850650808352039932
        N=0

        verts = (
            (-X,N,Z), (X,N,Z), (-X,N,-Z), (X,N,-Z),
            (N,Z,X), (N,Z,-X), (N,-Z,X), (N,-Z,-X),
            (Z,X,N), (-Z,X, N), (Z,-X,N), (-Z,-X, N)
        )

        faces = (
            0,4,1,0,9,4,9,5,4,4,5,8,4,8,1,
            8,10,1,8,3,10,5,3,8,5,2,3,2,7,3,
            7,10,3,7,6,10,7,11,6,11,0,6,0,1,6,
            6,1,10,9,0,11,9,11,2,9,2,5,7,2,11
        )
        colors = [color.random_color() for f in faces]
        print(colors)

        super().__init__(verts=verts, tris=faces, mode='tristrip', colors=colors, thickness=16, **kwargs)


class Cone(Mesh):
    def __init__(self, resolution=4, radius=.5, height=1, mode='triangle', **kwargs):
        origin = Entity()
        point = Entity(parent=origin)
        point.z = radius

        verts = list()
        for i in range(resolution):
            verts.append(point.world_position)
            verts.append((0,0,0))
            origin.rotation_y += 360 / resolution
            verts.append(point.world_position)

            origin.rotation_y -= 360 / resolution
            verts.append((0, height, 0))
            verts.append(point.world_position)
            origin.rotation_y += 360 / resolution
            verts.append(point.world_position)

        super().__init__(verts=verts, mode=mode, **kwargs)
        args = 'resolution='+str(resolution)+', '+'radius='+str(radius)+', '+'height='+str(height)
        self.constructor = self.__class__.__name__ + '('+args+')'



def duplicate(entity):
    e = entity.__class__()

    for name in entity.attributes:
        if name == 'model':
            e.model = eval(entity.model.constructor)
        elif name == 'scripts':
            pass
        else:
            if hasattr(entity, name):
                setattr(e, name, getattr(entity, name))

    return e


if __name__ == '__main__':
    app = Ursina()

    # e = Entity(
    #     # scale_x = 3,
    #     # model = Quad(size=(3,1), subdivisions=2, thickness=3, mode='lines'),
    #     model = Cone(),
    #     # model = 'cube',
    #     # texture = 'brick',
    #     texture_scale = (2,1),
    #     color = color.color(60,1,1,.3)
    #     )
    # e.scale *= 2
    # e1 = duplicate(e)
    # e1.y = -1
    for i in range(100):
        e = Entity(model = Cone(resolution=i), color = color.color(60,1,1,.3), x=i)
        e = Entity(model = Cone(resolution=i, mode='lines'), color = color.red, x=i)



    Entity(model='quad', color=color.orange, scale=(.05, .05))
    ed = EditorCamera(rotation_speed = 200, panning_speed=200)

    app.run()
