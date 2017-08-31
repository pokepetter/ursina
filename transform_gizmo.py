import sys
from pandaeditor import *


class TransformGizmo():

    def __init__(self):
        self.entity = None

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
        self.move_gizmo_x.parent = self.entity
        # print(self.move_gizmo_x.parent)
        self.move_gizmo_x.name = 'move_gizmo_x'
        self.move_gizmo_x.model = 'cube'
        self.move_gizmo_x.collider = 'box'
        self.move_gizmo_x.add_script('button')
        self.move_gizmo_x.add_script('move_gizmo')
        self.move_gizmo_x.color = color.red
        self.move_gizmo_x.scale = (.5, .1, .1)
        self.move_gizmo_x.x = .5


    def update(self, dt):
        # for moving stuff in side view
        if scene.editor.camera_pivot.rotation == (0,0,0) and self.dragging:
            if mouse.hovered_entity and mouse.hovered_entity.is_editor == False:
                if mouse.delta[0] != 0 or mouse.delta[1] != 0:
                    distance_to_camera = distance(
                        mouse.hovered_entity.getPos(camera.render),
                        camera.cam.getPos(camera.render)) * .2

                    mouse.hovered_entity.position = (
                        self.original_position[0] + (mouse.delta[0] * distance_to_camera * camera.aspect_ratio),
                        self.original_position[1] + (mouse.delta[1] * distance_to_camera),
                        self.original_position[2])

                    # print('newpos', mouse.hovered_entity.position)
        # if self.dragging_x:
        #     # print(mouse.delta[0] + mouse.delta[1])
        #     distance_to_camera = distance(
        #         self.entity.getPos(camera.render),
        #         camera.cam.getPos(camera.render))
        #
        #     self.entity.x = (
        #         self.original_position[0]
        #         + ((mouse.delta[0] + mouse.delta[1])
        #         * distance_to_camera * .35))

            # self.move_gizmo_x.position = self.entity.x  = .5


    def input(self, key):
        if key == 'left mouse down':
            if mouse.hovered_entity and mouse.hovered_entity.is_editor == False:
                self.original_position = mouse.hovered_entity.position
                self.dragging = True
                print('org pos', self.original_position)

            if mouse.hovered_entity:
                self.dragging_target = mouse.hovered_entity


            # select entities
            if mouse.hovered_entity and mouse.hovered_entity.is_editor == False:
                # print(mouse.hovered_entity.global_position)
                self.entity.position = mouse.hovered_entity.global_position
                if not self.add_to_selection:
                    scene.editor.selection.clear()
                    scene.editor.selection.append(mouse.hovered_entity)
                else:
                    scene.editor.selection.clear()

            #dragging the gizmo
            # self.original_transforms.clear()
            # self.original_position = self.entity.position

            if mouse.hovered_entity == self.move_gizmo_x:
                self.dragging_x = True
                # for selected in self.selection:
                #     self.original_transforms.append(selected.x)


        if key == 'left mouse up':
            #stop dragging
            self.original_position = mouse.hovered_entity.position
            self.dragging = False
            self.dragging_x = False
            self.dragging_y = False
            self.dragging_z = False


        if key == 'left shift':
            self.add_to_selection = True
        if key == 'left shift up':
            self.add_to_selection = False


        self.tool = self.tools.get(key, self.tool)

        if key == 'delete':
            for e in scene.editor.selection:
                destroy(e)



        if key == 'arrow left' and scene.editor.selection:
            if self.tool == 'move':
                for target in scene.editor.selection:
                    target.position += self.entity.left * self.move_interval
            elif self.tool == 'rotate':
                for target in scene.editor.selection:
                    target.rotation_z -= self.rotation_interval
            elif self.tool == 'scale':
                for target in scene.editor.selection:
                    target.scale_x += self.scale_interval

        if key == 'arrow right' and scene.editor.selection:
            if self.tool == 'move':
                for target in scene.editor.selection:
                    target.position += self.entity.right * self.move_interval
            elif self.tool == 'rotate':
                for target in scene.editor.selection:
                    target.rotation_z += self.rotation_interval
            elif self.tool == 'scale':
                for target in scene.editor.selection:
                    target.scale_x -= self.scale_interval

        if key == 'arrow up' and scene.editor.selection:
            if self.tool == 'move':
                for target in scene.editor.selection:
                    target.position += self.entity.up * self.move_interval
            elif self.tool == 'rotate':
                for target in scene.editor.selection:
                    target.rotation_x -= self.rotation_interval
            elif self.tool == 'scale':
                for target in scene.editor.selection:
                    target.scale_z += self.scale_interval

        if key == 'arrow down' and self.selection:
            if self.tool == 'move':
                for target in scene.editor.selection:
                    target.position += self.entity.down * self.move_interval
            elif self.tool == 'rotate':
                for target in scene.editor.selection:
                    target.rotation_x += self.rotation_interval
            elif self.tool == 'scale':
                for target in scene.editor.selection:
                    target.scale_z -= self.scale_interval
