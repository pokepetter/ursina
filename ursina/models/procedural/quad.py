from ursina import *

def rotate_point(point, origin, deg):
    from math import pi, cos, sin

    angle_rad = deg/180 * pi
    cos_angle = cos(angle_rad)
    sin_angle = sin(angle_rad)
    dx = point[0] - origin[0]
    dy = point[1] - origin[1]

    return (
        origin[0] + (dx*cos_angle - dy*sin_angle),
        origin[1] + (dx*sin_angle + dy*cos_angle)
        )

class Quad(Mesh):
    def __init__(self, radius=.1, segments=8, aspect=1, scale=(1,1), mode='ngon', **kwargs):
        super().__init__()
        self.vertices = [Vec2(0,0), Vec2(1,0), Vec2(1,1), Vec2(0,1)]
        self.radius = radius
        self.mode = mode

        segments += 1
        if segments > 1:
            self.vertices = [Vec2(radius,radius), Vec2(1-radius,radius), Vec2(1-radius,1-radius), Vec2(radius,1-radius)]
            offsets = [Vec2(-radius,0), Vec2(0,-radius), Vec2(radius,0), Vec2(0,radius)]
            new_verts = []

            for j, v in enumerate(self.vertices):
                point = v + offsets[j]
                new_verts.append(point)
                for i in range(segments):
                    point = rotate_point(point, v, 90/segments)
                    new_verts.append(Vec2(*point))

            self.vertices = new_verts


        self.uvs = list()
        for v in self.vertices:
            self.uvs.append((v[0], v[1]))

        # scale corners horizontally with aspect
        for v in self.vertices:
            if v[0] < .5:
                v[0] /= aspect
            else:
                v[0] = lerp(v[0], 1, 1-(1/aspect))

        # move edges out to keep nice corners
        for v in self.vertices:
            if v[0] > .5:
                v[0] += (scale[0]-1)
            if v[1] > .5:
                v[1] += (scale[1]-1)


        # center mesh
        offset = sum(self.vertices) / len(self.vertices)
        self.vertices = [Vec3(v[0]-offset[0], v[1]-offset[1], 0) for v in self.vertices]


        # make the line connect back to start
        if mode == 'line':
            self.vertices.append(self.vertices[0])

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.generate()




if __name__ == '__main__':
    app = Ursina()
    Entity(model=Quad(scale=(3,1), thickness=3, segments=3, mode='line'), color = color.color(0,1,1,.7))
    Entity(scale=(3,1), model=Quad(aspect=3), color = color.color(60,1,1,.3))
    origin = Entity(model='quad', color=color.orange, scale=(.05, .05))
    # ed = EditorCamera(rotation_speed = 200, panning_speed=200)
    camera.z = -5
    app.run()
