from ursina import *


class Quad(Mesh):
    def __init__(self, radius=.1, segments=3, aspect=1, scale=(1,1), mode='ngon', **kwargs):
        super().__init__()
        self.vertices = [Vec3(0,0,0), Vec3(1,0,0), Vec3(1,1,0), Vec3(0,1,0)]
        self.radius = radius
        self.mode = mode

        segments += 1
        if segments > 1:
            new_verts = list()
            corner_maker = Entity(add_to_scene_entities=False)
            point_placer = Entity(parent=corner_maker, x=-radius, add_to_scene_entities=False)
            corner_maker.rotation_z -= 90/segments/2

            corner_corrections = (Vec3(radius,radius,0), Vec3(-radius,radius,0), Vec3(-radius,-radius,0), Vec3(radius,-radius,0))
            for j in range(4):  # 4 corners
                corner_maker.position = self.vertices[j] + corner_corrections[j]
                for i in range(segments):
                    new_verts.append(point_placer.world_position)
                    corner_maker.rotation_z -= 90/segments

            destroy(corner_maker)
            destroy(point_placer)
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
        offset = average_position(self.vertices)
        self.vertices = [(v[0]-offset[0], v[1]-offset[1], v[2]-offset[2]) for v in self.vertices]


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
