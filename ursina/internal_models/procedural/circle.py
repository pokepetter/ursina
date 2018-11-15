from ursina import *


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
        super().__init__(vertices=verts, mode=mode, **kwargs)
        self.recipe = self.__class__.__name__ + '(resolution=' + str(resolution) + ', radius=' + str(radius) + ', mode=\'' + mode + '\')'



if __name__ == '__main__':
    app = Ursina()
    Entity(model=Circle(), color=color.color(60,1,1,.3), x=6)
    origin = Entity(model='quad', color=color.orange, scale=(.05, .05))
    ed = EditorCamera(rotation_speed = 200, panning_speed=200)
    app.run()
