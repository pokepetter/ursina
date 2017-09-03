import sys
sys.path.append("..")
from pandaeditor import *

class SelectionButton():

    def __init__(self):
        self.selection_target = None


    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            if self.selection_target:
                scene.editor.selection.clear()
                scene.editor.selection.append(self.selection_target)
            else:
                print('selection button selection_target not set')
