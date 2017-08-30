import sys
sys.path.append("..")
from pandaeditor import *

class MoveGizmo():

    def __init__(self):
        self.entity = None
        self.axis = None

    def input(self, key):
        # if key == 'left mouse down' and self.entity.hovered:
        return
        if key == 'left mouse up':
            print(mouse.delta[0])
            for t in self.entity.targets:
                if self.axis == 'x':
                    t.position_x += mouse.delta[0]
