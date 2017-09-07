import sys
sys.path.append("..")
from pandaeditor import *


class TransformGizmo(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'transform_gizmo'

        self.model = 'cube'
        self.rotation_x += 45
        self.rotation_y += 45
        self.rotation_z += 45
        self.scale *= .1
        self.color = color.green

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
        self.move_gizmo_x.parent = self
        self.move_gizmo_x.name = 'move_gizmo_x'
        self.move_gizmo_x.model = 'cube'
        self.move_gizmo_x.collider = 'box'
        self.move_gizmo_x.add_script('editor_button')
        self.move_gizmo_x.add_script('move_gizmo')
        self.move_gizmo_x.color = color.red
        self.move_gizmo_x.scale = (.5, .1, .1)
        self.move_gizmo_x.x = .5

        # scene.entities.append(self)
        self.scripts.append(self)
        self.button = None
        self.selection_buttons = list()



    def update(self, dt):
        # for moving stuff in side view
        if scene.editor.camera_pivot.rotation == (0,0,0) and self.dragging:
            # print(self.entity)
            if mouse.hovered_entity and mouse.hovered_entity.is_editor == False:
                if mouse.delta[0] != 0 or mouse.delta[1] != 0:
                    distance_to_camera = distance(
                        mouse.hovered_entity.getPos(camera.render),
                        camera.cam.getPos(camera.render)) * .2

                    for e in scene.editor.selection:
                        e.position = (
                            self.original_position[0] + (mouse.delta[0] * distance_to_camera * camera.aspect_ratio),
                            self.original_position[1] + (mouse.delta[1] * distance_to_camera),
                            self.original_position[2])

                    self.position = mouse.hovered_entity.global_position


    def input(self, key):
        if key == 'left mouse down':
            if mouse.hovered_entity and mouse.hovered_entity.is_editor == False:
                self.original_position = mouse.hovered_entity.position
                self.dragging = True

                # select entities
                self.position = mouse.hovered_entity.global_position
                if not self.add_to_selection:
                    scene.editor.selection.clear()
                    scene.editor.selection.append(mouse.hovered_entity)
                else:
                    scene.editor.selection.clear()

                # mouse.raycast = 0
            #dragging the gizmo
            # self.original_transforms.clear()
            # self.original_position = self.entity.position

            if mouse.hovered_entity == self.move_gizmo_x:
                self.dragging_x = True
                # for selected in self.selection:
                #     self.original_transforms.append(selected.x)

            self.entity_right_click_menu.enabled = False

        if key == 'left mouse up':
            #stop dragging
            self.original_position = mouse.hovered_entity.position
            self.dragging = False
            self.dragging_x = False
            self.dragging_y = False
            self.dragging_z = False
            # mouse.raycast = 1


        if key == 'left shift':
            self.add_to_selection = True
        if key == 'left shift up':
            self.add_to_selection = False

        if key == 'right mouse down':
            if mouse.hovered_entity:
                self.entity_right_click_menu.target = mouse.hovered_entity
                self.entity_right_click_menu.enabled = True
                self.entity_right_click_menu.position = mouse.position

# selection buttons
        if key == 't':
            entities = list(scene.entities)
            for e in entities:
                if not e.is_editor and e != camera and e != scene.ui:
                    self.button = load_prefab('editor_button')
                    self.button.is_editor = True
                    self.button.parent = scene.render
                    self.button.position = e.global_position
                    # self.button.position *= 2
                    # self.button.scale *= .01
                    self.button.text = e.name
                    self.button.look_at(camera)
                    # self.button.rotation_y += 180
                    # self.button.rotation_z += 180
                    # self.button.scale_z -= 1
                    # self.button.rotation = camera.rotation
                    # self.button.text_entity.scale *= .5
                    self.button.color = color.orange
                    self.button_script = self.button.add_script('selection_button')
                    self.button_script.selection_target = e
                    self.selection_buttons.append(self.button)
        if key == 't up':
            for b in self.selection_buttons:
                destroy(b)
            self.button = None
            self.button_script = None
            self.selection_buttons.clear()


        self.tool = self.tools.get(key, self.tool)

        if key == 'delete':
            for e in scene.editor.selection:
                destroy(e)


# move with arrow buttons
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
