import sys
sys.path.append("..")
from ursina import *

class MenuToggler():

    def __init__(self):
        self.target = None


    def on_click(self):
        # close menus before opening a new one
        # if self.entity.parent == scene.editor.load_menu_parent:
        #     for button in scene.editor.load_menu_parent.children:
        #         if button.menu_toggler:
        #             button.menu_toggler.target.enabled = False

        if self.target:
            self.target.enabled = not self.target.enabled
        else:
            for c in self.entity.children:
                c.enabled = not c.enabled
