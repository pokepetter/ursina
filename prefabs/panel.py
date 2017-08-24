import sys
sys.path.append("..")
from pandaeditor import *

class Panel(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'panel'
        self.parent = scene.ui
        self.model = 'quad'

    def __setattr__(self, name, value):
        if name == 'position':
            value = (value[0] / 2, (value[1] / 2), -.1)

        super().__setattr__(name, value)
