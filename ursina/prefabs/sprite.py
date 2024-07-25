from ursina import *

class Sprite(Entity):

    ppu = 100

    def __init__(self, texture=None, ppu:int=None, **kwargs):
        super().__init__()
        self.model = 'quad'
        self.texture = texture
        self.ppu = ppu if ppu else Sprite.ppu   # pixels per unit

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.update_scale()


    def update_scale(self):     # get called automatically on __init__, but if you change the texture or ppu, you can call this to update the scale.
        if not self.texture:
            return

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
