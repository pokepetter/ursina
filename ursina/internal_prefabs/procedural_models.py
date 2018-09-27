from ursina import *



class Cube(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'cube'

class Circle(Mesh):
    def __init__(self, resolution=16, radius=.5, rotate=True, mode='ngon', **kwargs):
        origin = Entity()
        point = Entity(parent=origin)
        point.y = radius

        verts = list()
        for i in range(resolution):
            origin.rotation_z -= 360 / resolution
            verts.append(point.world_position)

        destroy(origin)
        super().__init__(verts=verts, mode=mode, **kwargs)
        self.recipe = self.__class__.__name__ + '(resolution=' + str(resolution) + ', radius=' + str(radius) + ', mode=\'' + mode + '\')'


class Quad(Mesh):
    def __init__(self, size=(1,1), bevel=.05, subdivisions=0, ignore_aspect=False, **kwargs):
        self.verts = (Vec3(0,0,0), Vec3(1,0,0), Vec3(1,1,0), Vec3(0,1,0))
        self.bevel = bevel

        for j in range(subdivisions):
            points = list()
            for i, v in enumerate(self.verts):
                points.append(lerp(v, self.verts[i-1], bevel))
                next_index = i+1 if i+1 < len(self.verts) else 0
                points.append(lerp(v, self.verts[next_index], bevel))
                bevel += .005
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
        args = 'size='+str(size)+', bevel='+str(self.bevel)+', subdivisions='+str(subdivisions)+', ignore_aspect='+str(ignore_aspect)
        for k, v in kwargs.items():
            args += ', ' + k + '='
            if type(v) is str:
                args += '\'' + v + '\''
            else:
                args += str(v)
        self.recipe = self.__class__.__name__ + '('+args+')'


class Sphere(Mesh):
    def __init__(self, radius=.5, subdivision=0, mode='tristrip', **kwargs):
        X=.525731112119133606 * radius
        Z=.850650808352039932 * radius
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
        # colors = [color.random_color() for f in faces]
        colors = None
        # print(colors)

        super().__init__(verts=verts, tris=faces, colors=colors, mode=mode, **kwargs)
        args = 'radius='+str(radius)+', subdivision='+str(subdivision)+', mode=\''+mode + '\''
        for k, v in kwargs.items():
            args += ', ' + k + '='
            if type(v) is str:
                args += '\'' + v + '\''
            else:
                args += str(v)
        self.recipe = self.__class__.__name__ + '('+args+')'

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
        self.recipe = self.__class__.__name__ + '('+args+')'



if __name__ == '__main__':
    app = Ursina()

    e = Entity(
        # scale_x = 3,
        # model = Quad(size=(3,1), subdivisions=4, thickness=3, mode='lines'),
        # model = Cone(),
        model = Circle(),
        texture_scale = (2,1),
        color = color.color(60,1,1,.3)
        )
    # e.scale *= 2
    # e1 = duplicate(e)
    # e1.y = -1
    # for i in range(100):
    #     e = Entity(model = Cone(resolution=i), color = color.color(60,1,1,.3), x=i)
    #     e = Entity(model = Cone(resolution=i, mode='lines'), color = color.red, x=i)



    Entity(model='quad', color=color.orange, scale=(.05, .05))
    ed = EditorCamera(rotation_speed = 200, panning_speed=200)

    app.run()
