import sys
sys.path.append("..")
from pandaeditor import *

class MenuToggler():

    def __init__(self):
        self.is_editor = True
        self.target = None


    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            for button in scene.editor.toolbar.children:
                button.menu_toggler.target.enabled = False

            self.target.enabled = not self.target.enabled
