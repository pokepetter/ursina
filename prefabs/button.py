import sys
sys.path.append("..")
from pandaeditor import *

class Button(Entity):


    def __init__(self):
        super().__init__()
        self.name = 'button'
        self.parent = scene.ui.entity.node_path
        self.model = loader.loadModel('models/quad.egg')
        # self.scale = (0.5,0.5,0.5)
        self.collision = True
        self.collider = (self.model.getPos(scene.render), # pos
                        (0,0,0), # rot
                        (self.model.getScale(scene.render)[0] /4,
                        1,
                        self.model.getScale(scene.render)[2] /4))
        self.button_script = self.add_script('button')
        self.button_script.ui = scene.ui
        self.button_script.color = color.gray
        scene.entities.append(self)


    def __setattr__(self, name, value):
        if name == 'color':
            try:
                self.button_script.color = value
            except:
                pass
        if name == 'scale' and self.model:
            super().__setattr__(name, value)
            self.collider = (self.model.getPos(scene.render), (0,0,0),
                            (self.model.getScale(scene.render)[0] /4, 1,
                            self.model.getScale(scene.render)[2] /4))
            # print('updating collider:', self.collider)
        super().__setattr__(name, value)
