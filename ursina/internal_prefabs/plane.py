from ursina import *

class Plane(Entity):

    def __init__(self, size=1, **kwargs):
        super().__init__(**kwargs)
        self.name = 'plane'
        self.model = 'quad'
        self.rotation_x = 90
        if type(size) is int or type(size) is float:
            self.scale *= size
        else:
            self.scale = size

        for key, value in kwargs.items():
            setattr(self, key, value)



if __name__ == '__main__':
    app = ursina()
    test = Plane((10, 5), texture='white_cube', color=color.yellow)
    camera.position = (10, 10, 10)
    camera.look_at(test)
    app.run()
