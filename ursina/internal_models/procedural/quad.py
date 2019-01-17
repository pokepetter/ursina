from ursina import *


class Quad(Mesh):
    def __init__(self, size=(1,1), bevel=.1, subdivisions=0, ignore_aspect=False, mode='ngon', **kwargs):
        super().__init__()
        self.vertices = [Vec3(0,0,0), Vec3(1,0,0), Vec3(1,1,0), Vec3(0,1,0)]
        self.bevel = bevel
        self.mode = mode

        subdivisions += 1
        if subdivisions > 1:
            new_verts = list()
            corner_maker = Entity()
            point_placer = Entity(parent=corner_maker, x=-bevel)
            corner_maker.rotation_z -= 90/subdivisions/2

            corner_corrections = (Vec3(bevel,bevel,0), Vec3(-bevel,bevel,0), Vec3(-bevel,-bevel,0), Vec3(bevel,-bevel,0))
            for j in range(4):  # 4 corners
                corner_maker.position = self.vertices[j] + corner_corrections[j]
                for i in range(subdivisions):
                    new_verts.append(point_placer.world_position)
                    corner_maker.rotation_z -= 90/subdivisions

            self.vertices = new_verts


        self.uvs = list()
        for v in self.vertices:
            self.uvs.append((v[0], v[1]))

        # move edges out like a 9 slice
        for v in self.vertices:
            if v[0] <= (1/3):
                v[0] -= (size[0] - 1) / 4
            if v[0] >= (2/3):
                v[0] += (size[0] - 1) / 4

            if v[1] <= (1/3):
                v[1] -= (size[1] - 1) / 4
            if v[1] >= (2/3):
                v[1] += (size[1] - 1) / 4


        # make the line connect back to start

        # center mesh
        offset = average_position(self.vertices)
        self.vertices = [(v[0]-offset[0], v[1]-offset[1], v[2]-offset[2]) for v in self.vertices]


        if mode == 'lines':
            self.vertices.append(self.vertices[0])

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.generate()

        args = 'size='+str(size)+', bevel='+str(self.bevel)+', subdivisions='+str(subdivisions)+', ignore_aspect='+str(ignore_aspect)
        for k, v in kwargs.items():
            args += ', ' + k + '='
            if type(v) is str:
                args += '\'' + v + '\''
            else:
                args += str(v)
        self.recipe = self.__class__.__name__ + '('+args+')'



if __name__ == '__main__':
    app = Ursina()
    Entity(model=Quad(size=(3,1), thickness=3, subdivisions=3, mode='lines'), color = color.color(0,1,1,.7))
    Entity(model=Quad(size=(3,1)), color = color.color(60,1,1,.3))
    origin = Entity(model='quad', color=color.orange, scale=(.05, .05))
    # ed = EditorCamera(rotation_speed = 200, panning_speed=200)
    camera.z = -5
    app.run()
