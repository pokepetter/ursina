import sys
sys.path.append("..")
from pandaeditor import *

class Button():

    def __init__(self):
        self.entity = Entity()
        self.entity.name = 'button'
        self.entity.parent = ui_entity.node_path
        self.entity.model = loader.loadModel('models/quad_rounded.egg')
        # tex = loader.loadTexture('textures/winter_forest.png')
        # self.entity.model.setTexture(tex, 1)

        self.entity.position = (0.25, 0, 0.0)
        self.entity.scale = (.25, 1, 0.5)
        # self.entity.origin = (-1, 0, 0)
        self.entity.collision = True
        self.entity.collider = (self.entity.node_path.getPos(self.render), (0,0,0),
                        (self.entity.model.getScale(self.render)[0] /4, 1,
                        self.entity.model.getScale(self.render)[2] /4))

        button_script = self.entity.add_script('button')
        button_script.ui = ui_main
        button_script.color = color.gray
        button_script.set_up()
        self.entities.append(self.entity)

    
