from ursina import *

class Sprite(Entity):

    ppu = 100

    def __init__(self, texture=None, ppu=ppu, **kwargs):
        super().__init__(**kwargs)
        self.model = 'quad'
        self.texture = texture
        self.ppu = ppu

        for key, value in kwargs.items():
            setattr(self, key, value)

        if not self.texture:
            # destroy(self)
            return None

        self.scale_y *= self.texture.height / self.ppu
        self.aspect_ratio = self.texture.width / self.texture.height
        self.scale_x = self.scale_y * self.aspect_ratio


if __name__ == '__main__':
    app = Ursina()
    camera.orthographic = True
    camera.fov = 1
    Sprite.ppu = 16
    Texture.default_filtering = None
    s = Sprite('brick', filtering=False)
    app.run()
