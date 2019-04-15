from ursina import *


class Cone(Mesh):
    def __init__(self, resolution=4, radius=.5, height=1, direction=(0,1,0), mode='triangle', **kwargs):
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

        super().__init__(vertices=verts, mode=mode, **kwargs)
        args = 'resolution='+str(resolution)+', '+'radius='+str(radius)+', '+'height='+str(height)
        self.recipe = self.__class__.__name__ + '('+args+')'


if __name__ == '__main__':
    app = Ursina()
    Entity(model=Cone(8), color=color.color(60,1,1,.3), x=2)
    origin = Entity(model='quad', color=color.orange, scale=(.05, .05))
    ed = EditorCamera(rotation_speed = 200, panning_speed=200)
    app.run()
