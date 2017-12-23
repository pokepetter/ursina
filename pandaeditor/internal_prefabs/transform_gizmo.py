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

        self.button = None
        self.selection_buttons = list()

        self.trash_list = list()


    @undoable
    def move_from_to(self, entities, original_positions, new_positions):
        for i in range(len(entities)):
            entities[i].position = new_positions[i]

        # undo
        yield 'move selected'
        print('move back from:', new_positions[0], 'to:', original_positions[0])
        for i in range(len(entities)):
            entities[i].position = original_positions[i]



    @undoable
    def delete_selected(self):
        self.trash_list.append([e for e in scene.editor.selection])
        print(self.trash_list[-1])
        for e in self.trash_list[-1]:
            e.parent_before_destroyed = e.parent
            e.enabled = False
            e.parent = None
            print('m')

        scene.editor.entity_list.populate()
        print(self.trash_list)

        yield 'delete selected'
        print('restore detached')
        # get prev from trash can
        for e in self.trash_list[-1]:
            e.parent = e.parent_before_destroyed
            e.enabled = True
            # scene.editor.selection.append(e)

        del self.trash_list[-1]
        print('trash list is now:', self.trash_list)

        scene.editor.entity_list.populate()


    def update(self, dt):
        if not scene.editor.enabled:    # just to make sure
            return
        # for moving stuff in side view
        if (scene.editor.camera_pivot.rotation == (0,0,0)
        and mouse.hovered_entity
        and mouse.hovered_entity.is_editor == False):

            if mouse.delta_drag[0] != 0 or mouse.delta_drag[1] != 0 and mouse.left:
                dist_to_cam = distance(
                    mouse.hovered_entity.getPos(camera.render),
                    camera.cam.getPos(camera.render)) * .2

                for e in scene.editor.selection:
                    e.position = (
                        self.position[0] + (mouse.delta[0] * dist_to_cam * camera.aspect_ratio),
                        self.position[1] + (mouse.delta[1] * dist_to_cam),
                        self.position[2])
                    e.position = (round(e.x, 2), round(e.y, 2), round(e.z, 2))


    def input(self, key):
        if key == 'left mouse down':
            if not mouse.hovered_entity:
                scene.editor.selection.clear()

            elif mouse.hovered_entity.is_editor == False:
                # select entities
                if not self.add_to_selection:
                    scene.editor.selection.clear()
                    scene.editor.selection.append(mouse.hovered_entity)
                else:
                    scene.editor.selection.clear()

                self.start_drag_position = mouse.position
                self.position = scene.editor.selection[-1].global_position
                print('start drag:', self.start_drag_position)

                self.temp_original_positions = [p.position for p in scene.editor.selection]


        if key == 'left mouse up':
            self.new_positions = [p.position for p in scene.editor.selection]
            if mouse.delta_drag[0] != 0 or mouse.delta_drag[1] != 0:   # check if actually moved
                self.original_positions = self.temp_original_positions
                print('drop:', mouse.delta_drag[0])
                print('move', self.new_positions[0], self.original_positions[0])

                self.move_from_to(
                    [e for e in scene.editor.selection],
                    self.original_positions,
                    self.new_positions
                    )

                self.position = scene.editor.selection[-1].global_position


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
                if not e.is_editor and e is not camera and e is not scene.ui:
                    self.button = EditorButton()
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
            self.delete_selected()


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
