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
        self.editor_collider = 'box'
        

    def start(self):
        self.original_parent = self.parent
        self.original_scale = self.scale
        self.parent = scene.ui
        self.parent = original_parent
        self.scale = original_scale


    def stop(self):
        self.parent = self.original_parent
        self.position = (0,0,0)
