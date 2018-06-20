from ursina import *


class TransformGizmo(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'transform_gizmo'

        self.model = 'cube'
        self.scale *= .1
        self.color = color.lime

        self.add_to_selection = False
        self.entity_to_scale = None
        self.dist_to_cam = 0
        self.tool = 'none'
        self.tools = {
            'q' : 'none',
            'w' : 'move',
            'e' : 'rotate',
            'r' : 'scale'
            }

        self.button = None
        self.selection_buttons = list()

        self.prev_positions = list()
        self.original_parent = list()
        self.trash_list = list()


    @undoable
    def move_entities(self, entities):
        # save these for undo
        # self.selection_copy = [e for e in entities]
        # self.prev_positions = [e.position for e in entities]
        self.temp_delta = mouse.delta
        self.prev_positions.append([e.position for e in entities])


        for e in entities:
            e.position = (
                e.position[0] + (mouse.delta[0] * self.dist_to_cam * camera.aspect_ratio),
                e.position[1] + (mouse.delta[1] * self.dist_to_cam),
                e.position[2])
            e.position = (round(e.x, 2), round(e.y, 2), round(e.z, 2))

        # print(entities[0].name, 'from:', self.prev_positions[-1][0], 'to:', entities[0].position)

        # undo
        yield 'move selected'
        print('redo move')
        for i, e in enumerate(entities):
            e.position = self.prev_positions[-1][i]

        self.prev_positions.pop()
        print(len(self.prev_positions))


    @undoable
    def delete_selected(self):
        self.trash_list.append([e for e in scene.editor.selection])
        print(self.trash_list[-1])
        for e in self.trash_list[-1]:
            e.parent_before_destroyed = e.parent
            e.enabled = False
            e.parent = None
            print('m')

        scene.editor.hierarchy_panel.populate()
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

        scene.editor.hierarchy_panel.populate()


    def update(self, dt):
        if not scene.editor.enabled:    # just to make sure
            return
        # if mouse.hovered_entity.is_editor:
        #     return
        # for moving stuff in side view
        if (scene.editor.editor_camera.camera_pivot.rotation == (0,0,0)
        and mouse.hovered_entity
        and mouse.hovered_entity.is_editor == False
        and mouse.left):

            if mouse.delta_drag[0] != 0 or mouse.delta_drag[1] != 0:
                self.dist_to_cam = distance(
                    mouse.hovered_entity.get_pos(camera.render),
                    camera.cam.get_pos(camera.render)) * .2

                for i, e in enumerate(scene.editor.selection):
                    e.position = (
                        self.position[0] + (mouse.delta[0] * self.dist_to_cam * camera.aspect_ratio),
                        self.position[1] + (mouse.delta[1] * self.dist_to_cam),
                        self.position[2])
                    e.position = (round(e.x, 2), round(e.y, 2), round(e.z, 2))


# scale
        if self.entity_to_scale:
            self.entity_to_scale.scale = self.entity_original_scale * (1 + (mouse.x - self.start_mouse) * 4)
            self.entity_to_scale.scale = [round(s, 2) for s in self.entity_to_scale.scale]



    def input(self, key):
        if key == 'left mouse down':
            if mouse.hovered_entity and mouse.hovered_entity.is_editor:
                return
            if not mouse.hovered_entity:
                scene.editor.selection.clear()

            elif mouse.hovered_entity and mouse.hovered_entity.is_editor == False:
                # select entities
                if not self.add_to_selection:
                    scene.editor.selection.clear()
                    scene.editor.selection.append(mouse.hovered_entity)
                else:
                    scene.editor.selection.clear()

                if len(scene.editor.selection) > 0:
                    self.position = scene.editor.selection[-1].world_position
                    self.start_positions = [e.position for e in scene.editor.selection]
                    self.original_parents = [e.parent for e in scene.editor.selection]
                    for e in scene.editor.selection:
                        e.reparent_to(scene)


        if key == 'left mouse up':
            if mouse.hovered_entity and mouse.hovered_entity.is_editor:
                return

            for i, e in enumerate(scene.editor.selection):
                # self.original_parent = e.position
                # e.reparent_to(scene)
                e.parent = self.original_parents[i]
                e.position = self.start_positions[i]
                # e.reparent_to(self.original_parent)

            self.move_entities(scene.editor.selection)
            if len(scene.editor.selection) > 0:
                self.position = scene.editor.selection[-1].world_position
            # scene.editor.selection.clear()



        if key == 'left shift':
            self.add_to_selection = True
        if key == 'left shift up':
            self.add_to_selection = False


        if key == 's' and not held_keys['control']:
            if scene.editor.selection[0]:
                self.start_mouse = mouse.x
                self.entity_to_scale = scene.editor.selection[0]
                print(self.entity_to_scale)
                self.entity_original_scale = self.entity_to_scale.scale
        if key == 's up':
            # self.entity_to_sale
            self.entity_to_scale = None

# selection buttons
        if key == 't':
            entities = list(scene.entities)
            for e in entities:
                if not e.is_editor and e is not camera and e is not scene.ui:
                    self.button = EditorButton()
                    self.button.is_editor = True
                    self.button.parent = render
                    self.button.position = e.world_position
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
