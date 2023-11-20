from ursina import *


class Background(Entity):

    def __init__(self, **kwargs):
        from ursina.shaders import unlit_shader
        super().__init__(name='sky', model='sky_dome', texture='sky_default', shader=unlit_shader)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        self.world_position = camera.world_position


if __name__ == '__main__':
    app = Ursina()

    Background(texture='sky_sunset')

    app.run()
