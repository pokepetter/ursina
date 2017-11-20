import sys
sys.path.append("..")
from pandaeditor import *

class NewScriptButton():

    def __init__(self):
        self.is_editor = True
        self.target = None


    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            self.target.enabled = not self.target.enabled
