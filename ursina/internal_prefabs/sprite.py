from ursina import *

class Sprite(Entity):
    def __init__(self, texture=None, **kwargs):
        super().__init__(**kwargs)
        self.model = 'quad'
        self.texture = texture
        if not hasattr(self, 'texture'): #self.texture:
            print('tolo')
            destroy(self)
            return None

        self.aspect_ratio = self.texture_width / self.texture_height
        self.scale_x = self.scale_y * self.aspect_ratio


if __name__ == '__main__':
    app = Ursina()
    s = Sprite('panda_button')
    # print(s.texture_path)
    # print(s.get_pixel(0,0))
    # print(s.pixels)
    app.run()
