import sys
sys.path.append("..")
from pandaeditor import *

class Canvas(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'canvas'
        self.model = 'canvas'
        self.origin = (0, 0, -.01)
        self.color = color.white33
        self.add_script('canvas')
        self.editor_collider = 'box'
