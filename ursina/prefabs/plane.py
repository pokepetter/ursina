from ursina import *

class Plane(Entity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'plane'
        self.model = 'quad'
        self.rotation_x = 90

        for key, value in kwargs.items():
            setattr(self, key, value)



if __name__ == '__main__':
    app = Ursina()
    plane = Plane(scale=(10, 5), texture='white_cube', color=color.yellow)
    # camera.position = (10, 10, 10)
    # camera.look_at(test)
    app.run()
