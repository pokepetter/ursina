import sys
sys.path.append("..")
from pandaeditor import *

class ToggleSideview():

    def __init__(self):
        self.sideview = False

    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:

            scene.editor.camera_pivot.rotation = (0,0,0)
