import sys
sys.path.append("..")
from pandaeditor import *

class TransformGizmo():

    def __init__(self):
        self.entity = None

        # self.move_x = load_model('arrow_x')


    def input(self, key):
        if key == 'left mouse down' and mouse.hovered_entity:
            print(mouse.hovered_entity.global_position)
            self.entity.position = mouse.hovered_entity.global_position
