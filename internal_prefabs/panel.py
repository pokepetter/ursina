import sys
sys.path.append("..")
from pandaeditor import *

class Panel(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'panel'
        self.parent = scene.ui
        self.model = 'quad'
        self.color = color.panda_button
