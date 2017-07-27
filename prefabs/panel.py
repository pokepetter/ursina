import sys
sys.path.append("..")
from pandaeditor import *

class Panel(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'panel'
        self.parent = scene.ui.entity.node_path
        self.model = 'quad'
        scene.entities.append(self)
        # print('created panel')

    def __setattr__(self, name, value):
        if name == 'position':
            value = (value[0] / 2, (value[1] / 2) - .1, value[2] / 2)
        super().__setattr__(name, value)
