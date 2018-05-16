from pandaeditor import *

class Sprite(Entity):
    def __init__(self, texture=None, **kwargs):
        super().__init__(**kwargs)
        self.model = 'quad'
        self.texture = texture
        if not hasattr(self, 'texture'): #self.texture:
            print('tolo')
            destroy(self)
            return None

        self.aspect_ratio = self.model.getTexture().getOrigFileXSize() / self.model.getTexture().getOrigFileYSize()
        self.scale_x = self.scale_y * self.aspect_ratio


if __name__ == '__main__':
    app = PandaEditor()
    s = Sprite('panda_buttons')
    app.run()
