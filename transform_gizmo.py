import sys
sys.path.append("..")
from pandaeditor import *

class TransformGizmo():

    def __init__(self):
        self.entity = None

        self.targets = list()
        self.add_to_selection = False

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

        self.move_gizmo_x = Entity()
        self.move_gizmo_x.is_editor = True
        self.move_gizmo_x.name = 'move_gizmo_x'
        self.move_gizmo_x.model = 'cube'
        self.move_gizmo_x.add_script('button')
        self.move_gizmo_x.add_script('move_gizmo')
        self.move_gizmo_x.color = color.red
        self.move_gizmo_x.scale = (.5, .1, 1.)
        self.move_gizmo_x.x = .5


    def input(self, key):
        if key == 'left mouse down':
            if mouse.hovered_entity and not mouse.hovered_entity.is_editor:
                # print(mouse.hovered_entity.global_position)
                self.entity.position = mouse.hovered_entity.global_position
                print(entity.name)
                if not self.add_to_selection:
                    self.targets.clear()

                self.targets.append(mouse.hovered_entity)
            else:
                self.targets.clear()

        if key == 'left shift':
            self.add_to_selection = True
        if key == 'left shift up':
            self.add_to_selection = False


        self.tool = self.tools.get(key, self.tool)


        print(self.targets)

        if key == 'arrow left' and self.targets:
            if self.tool == 'move':
                for target in self.targets:
                    target.position += self.entity.left * self.move_interval
            elif self.tool == 'rotate':
                for target in self.targets:
                    target.rotation_z -= self.rotation_interval
            elif self.tool == 'scale':
                for target in self.targets:
                    target.scale_x += self.scale_interval

        if key == 'arrow right' and self.targets:
            if self.tool == 'move':
                for target in self.targets:
                    target.position += self.entity.right * self.move_interval
            elif self.tool == 'rotate':
                for target in self.targets:
                    target.rotation_z += self.rotation_interval
            elif self.tool == 'scale':
                for target in self.targets:
                    target.scale_x -= self.scale_interval

        if key == 'arrow up' and self.targets:
            if self.tool == 'move':
                for target in self.targets:
                    target.position += self.entity.up * self.move_interval
            elif self.tool == 'rotate':
                for target in self.targets:
                    target.rotation_x -= self.rotation_interval
            elif self.tool == 'scale':
                for target in self.targets:
                    target.scale_z += self.scale_interval

        if key == 'arrow down' and self.targets:
            if self.tool == 'move':
                for target in self.targets:
                    target.position += self.entity.down * self.move_interval
            elif self.tool == 'rotate':
                for target in self.targets:
                    target.rotation_x += self.rotation_interval
            elif self.tool == 'scale':
                for target in self.targets:
                    target.scale_z -= self.scale_interval
