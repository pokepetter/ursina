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

        if mode == 'line':  # add the first point to make the circle whole
            verts.append(verts[0])

        destroy(origin)
        super().__init__(vertices=verts, mode=mode, **kwargs)


if __name__ == '__main__':
    app = Ursina()
    e = Entity(model=Circle(8, mode='line', thickness=10), color=color.color(60,1,1,.3), x=6)
    print(e.model.recipe)
    origin = Entity(model='quad', color=color.orange, scale=(.05, .05))
    ed = EditorCamera(rotation_speed = 200, panning_speed=200)
    app.run()
