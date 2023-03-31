from ursina import *


class Circle(Mesh):
    def __init__(self, resolution=16, radius=.5, mode='ngon', **kwargs):
        origin = Entity()
        point = Entity(parent=origin)
        point.y = radius

        self.vertices = list()
        for i in range(resolution):
            origin.rotation_z -= 360 / resolution
            self.vertices.append(point.world_position)

        if mode == 'line':  # add the first point to make the circle whole
            self.vertices.append(self.vertices[0])

        destroy(origin)
        super().__init__(vertices=self.vertices, mode=mode, **kwargs)


if __name__ == '__main__':
    app = Ursina()
    e = Entity(model=Circle(8, mode='line', thickness=10), color=color.color(60,1,1,.3))
    print(e.model.recipe)
    origin = Entity(model='quad', color=color.orange, scale=(.05, .05))
    ed = EditorCamera(rotation_speed = 200, panning_speed=200)
    app.run()
