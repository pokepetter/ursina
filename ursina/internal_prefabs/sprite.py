from ursina import *

class Sprite(Entity):
    def __init__(self, texture=None, **kwargs):
        super().__init__(**kwargs)
        self.model = 'quad'
        self.texture = texture

        for key, value in kwargs.items():
            setattr(self, key, value)
            if key == 'texture':
                self.texture = value

        if not self.texture:
            destroy(self)
            return None

        self.aspect_ratio = self.texture_width / self.texture_height
        self.scale_x = self.scale_y * self.aspect_ratio


if __name__ == '__main__':
    app = Ursina()
    s = Sprite(texture = 'panda_button')
    print(s.scale * 2)
    s.scale *= 2
    app.run()
