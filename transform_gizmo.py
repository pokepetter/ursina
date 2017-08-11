import sys
sys.path.append("..")
from pandaeditor import *

class TransformGizmo():

    def __init__(self):
        self.entity = None
        self.tool = 'none'
        self.tools = {
            'q' : 'none',
            'w' : 'move',
            'e' : 'rotate',
            'r' : 'scale'
            }
        self.move_interval = 1
        self.rotation_interval = 5
        self.scale_interval = .1


    def input(self, key):
        if key == 'left mouse down':
            if mouse.hovered_entity and not mouse.hovered_entity.is_editor:
                print(mouse.hovered_entity.global_position)
                self.entity.position = mouse.hovered_entity.global_position
                self.target = mouse.hovered_entity
            else:
                self.target = None


        self.tool = self.tools.get(key, self.tool)

        if self.tool != 'none':
            print(self.tool)

        if key == 'arrow left' and self.target:
            if self.tool == 'move':
                self.target.position += self.entity.left * self.move_interval
            elif self.tool == 'rotate':
                self.target.rotation_z -= self.rotation_interval
            elif self.tool == 'scale':
                self.target.scale_x += self.scale_interval
                print('saglkaega:', scene.grid.scale)

        if key == 'arrow right' and self.target:
            if self.tool == 'move':
                self.target.position += self.entity.right * self.move_interval
            elif self.tool == 'rotate':
                self.target.rotation_z += self.rotation_interval
            elif self.tool == 'scale':
                self.target.scale_x -= self.scale_interval

        if key == 'arrow up' and self.target:
            if self.tool == 'move':
                self.target.position += self.entity.up * self.move_interval
            elif self.tool == 'rotate':
                self.target.rotation_x -= self.rotation_interval
            elif self.tool == 'scale':
                self.target.scale_z += self.scale_interval
                print('saglkaega:', scene.grid.scale)

        if key == 'arrow down' and self.target:
            if self.tool == 'move':
                self.target.position += self.entity.down * self.move_interval
            elif self.tool == 'rotate':
                self.target.rotation_x += self.rotation_interval
            elif self.tool == 'scale':
                self.target.scale_z -= self.scale_interval
