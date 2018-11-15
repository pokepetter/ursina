from ursina import *


class Quad(Mesh):
    def __init__(self, size=(1,1), bevel=.05, subdivisions=0, ignore_aspect=False, **kwargs):
        super().__init__()
        self.vertices = (Vec3(0,0,0), Vec3(1,0,0), Vec3(1,1,0), Vec3(0,1,0))
        self.bevel = bevel

        for j in range(subdivisions):
            points = list()
            for i, v in enumerate(self.vertices):
                points.append(lerp(v, self.vertices[i-1], bevel))
                next_index = i+1 if i+1 < len(self.vertices) else 0
                points.append(lerp(v, self.vertices[next_index], bevel))
                bevel += .005
            self.vertices = points

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
        if 'mode' in kwargs and kwargs['mode'] == 'lines':
            self.vertices.append(self.vertices[0])

        # center mesh
        offset = average_position(self.vertices)
        self.vertices = [(v[0]-offset[0], v[1]-offset[1], v[2]-offset[2]) for v in self.vertices]

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
    Entity(model=Quad(size=(3,1), subdivisions=4, thickness=3), color = color.color(60,1,1,.3))
    origin = Entity(model='quad', color=color.orange, scale=(.05, .05))
    ed = EditorCamera(rotation_speed = 200, panning_speed=200)
    app.run()
