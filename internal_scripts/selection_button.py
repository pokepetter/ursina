import sys
sys.path.append("..")
from pandaeditor import *

class SelectionButton():

    left_shift = False

    def __init__(self):
        self.entity = None
        self.selection_target = None
        self.dragging = False

    def input(self, key):
        if key == 'left shift':
            left_shift = True
        if key == 'left shift up':
            left_shift = False


        if key == 'left mouse down' and self.entity.hovered:
            print('down')
            self.dragging = True
            if self.selection_target:
                # if not left_shift:
                scene.editor.selection.clear()

                print('selecting:', self.selection_target)
                scene.editor.selection.append(self.selection_target)
            else:
                print('selection button selection_target not set')




        if key == 'left mouse up':
            self.dragging = False

    def update(self, dt):
        if self.dragging:
            # print('updateing slection button')
            print(self.entity.scale[1])
            print(mouse.delta[1])
            if mouse.delta[1] > self.entity.scale[1]:
                pass
