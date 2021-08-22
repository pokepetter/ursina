from ursina import *


class EditorIcon(Draggable):
    def __init__(self, **kwargs):
        super().__init__(
            parent=scene,
            world_scale=.25,
            always_on_top=True,
            plane_direction=(0,1,0),
            require_key='w',
            add_to_scene_entities=False,
            model='diamond',
            color=color.white,
            )

        for key, value in kwargs.items():
            setattr(self, key ,value)

        self.text = 'entity'
        self.text_entity.y = 1
        self.text_entity.scale = 2
        self.text_entity.enabled = self.scene_editor.show_names

    def drag(self):
        self.always_on_top = False
        if not self.scene_editor.selection and not held_keys['alt']: # nothing selected, so just move this one
            self.scene_editor.selection.append(self)

        for icon in self.scene_editor.selection:
            icon.entity.original_parent = icon.entity.parent
            icon.entity._start_position = icon.entity.position
            icon.entity.world_parent = self



    def drop(self):
        self.always_on_top = True
        for icon in self.scene_editor.selection:
            icon.entity.world_parent = icon.entity.original_parent

        s = Sequence(*(Func(setattr, icon.entity, 'world_position', icon.entity._start_position) for icon in self.scene_editor.selection))
        self.scene_editor.record_undo(s)


class AssetMenu(ButtonList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scrollable = self.add_script(Scrollable(min=self.y, max=len(self.button_dict) * self.button_height))


    def on_enable(self):
        self.scene_editor.editor_camera.ignore = True
        self.y = mouse.y

    def on_disable(self):
        self.scene_editor.editor_camera.ignore = False

    def input(self, key):
        super().input(key)
        if key == 'left mouse down':
            if not mouse.hovered_entity or not mouse.hovered_entity.has_ancestor(self):
                self.enabled = False


class SelectionBox(Entity):
    def input(self, key):
        if key == 'left mouse down' and not held_keys['w']:
            self.position = mouse.position
            self.scale = .001
            self.visible = True
            self.mode = 'new'
            if held_keys['shift']:
                self.mode = 'add'
            if held_keys['alt']:
                self.mode = 'subtract'

        if key == 'left mouse up':
            self.visible = False

            if self.scale_x < 0:
                self.x += self.scale_x
                self.scale_x = abs(self.scale_x)
            if self.scale_y < 0:
                self.y += self.scale_y
                self.scale_y = abs(self.scale_y)

            if self.scale_x < .01 or self.scale_y < .01 or held_keys['w']:
                return

            if self.mode == 'new':
                self.scene_editor.clear_selection()

            for icon in self.scene_editor.editor_icons:

                pos = icon.screen_position
                if pos.x > self.x and pos.x < self.x + abs(self.scale_x) and pos.y > self.y and pos.y < self.y + abs(self.scale_y):
                    if self.mode != 'subtract' and not icon in self.scene_editor.selection:
                        self.scene_editor.selection.append(icon)

                    elif icon in self.scene_editor.selection:
                        self.scene_editor.selection.remove(icon)

            self.scene_editor.render_selection()
            self.mode = 'new'

    def update(self):
        if mouse.left:
            if mouse.x == mouse.start_x and mouse.y == mouse.start_y:
                return

            self.scale_x = mouse.x - self.x
            self.scale_y = mouse.y - self.y


class SceneEditor(Entity):
    def __init__(self):
        super().__init__()
        self.world_grid = Entity(parent=self, model=Grid(32,32), scale=32, rotation_x=90, color=color.white33, collider='box', collision=False)

        self.help_text = Text(x=-.5*camera.aspect_ratio, text=dedent('''
            w : move
            e : scale individual
            s : scale from pivot
            c : scale from center
            x/y/z : move on axis
            ctrl + g : group selection
            F2 : rename
            m : select model
            t : select texture
            '''),
            origin=(-.5,0)
            )
        self.cursor_3d = Entity(parent=self, model=Mesh(vertices=[(0,0,0)], mode='point', thickness=10), color=color.pink, visible=True)
        line_model = Mesh(vertices=((-1,0,0), (1,0,0)), mode='line', thickness=2)
        self.cursor_3d.rulers = (
            Entity(parent=self.cursor_3d, model=copy(line_model), scale_x=999, color=color.magenta, enabled=False, add_to_scene_entities=False),
            Entity(parent=self.cursor_3d, model=copy(line_model), scale_x=999, color=color.yellow, rotation_z=90, enabled=False, add_to_scene_entities=False),
            Entity(parent=self.cursor_3d, model=copy(line_model), scale_x=999, color=color.cyan, rotation_y=90, enabled=False, add_to_scene_entities=False),
        )
        self.editor_camera = EditorCamera()

        self.entities = list()
        self.editor_icon_parent = Entity()
        self.editor_icons = list()
        self.selection = list()
        self.selection_text = Text(position=window.top_left, origin=(-.5,.5), text='Selection:')
        self.selection_box = SelectionBox(scene_editor=self, parent=camera.ui, model=Quad(0, mode='line'), origin=(-.5,-.5,0), scale=(0,0,1), color=color.white33)

        self.duplicate_dragger = Draggable(parent=scene, model='plane', plane_direction=(0,1,0), enabled=False)
        def drop(self=self):
            for e in self.duplicate_dragger.children:
                e.world_parent = e.original_parent
                # e.world_parent = scene
            self.duplicate_dragger.enabled = False
        self.duplicate_dragger.drop = drop

        self.models = [e.stem for e in application.internal_models_compressed_folder.glob('**/*.ursinamesh')]
        for file_type in ('.bam', '.obj', '.ursinamesh'):
            self.models += [e.stem for e in application.asset_folder.glob(f'**/*.{file_type}') if not 'animation' in e]
        self.model_menu = AssetMenu(button_dict={key : Func(self.set_attr_for_selected, 'model', key) for key in self.models}, scene_editor=self, enabled=False)

        self.textures = []
        for file_type in ('.png', '.jpg', '.gif', '.psd'):
            self.textures += [e.stem for e in application.asset_folder.glob(f'**/*{file_type}') if not e.stem in self.textures]
            # self.textures += [e.stem for e in application.internal_textures_folder.glob(f'**/*{file_type}') if not e.stem in self.textures]
            self.textures += [e for e in ('white_cube', 'brick') if not e in self.textures]
        self.texture_menu = AssetMenu(button_dict={key : Func(self.set_attr_for_selected, 'texture', key) for key in self.textures}, scene_editor=self, enabled=False)

        self.rename_window = WindowPanel(title='Rename', enabled=False, popup=True,
            content=(
                InputField(name='name'),
                Button(text='Rename', color=color.azure, on_click=self.rename_selected),
            ),
        )
        self.scene_name = 'untitled'
        self.scene_folder = application.asset_folder / 'scenes'
        self.ask_for_scene_name_window = WindowPanel(title='Enter scene name', enabled=False, popup=True,
            content=(
                InputField(name='scene name'),
                Button(text='Save', color=color.azure, on_click=self.save),
            ),
        )
        self.menus = [self.model_menu, self.texture_menu, self.rename_window, self.ask_for_scene_name_window]
        self.show_names = False

        # self.tool = 'move'

        self.load('test3')

        self.undo_cache = list()

        self.undo_index = 0
        self.record_undo()
        self.undo_index = 0


    def record_undo(self, undo_data=None):
        # record undo
        self.undo_index += 1
        print(self.undo_index)
        self.undo_cache = self.undo_cache[:self.undo_index]


        if undo_data is None:
            undo_data = dict()
            for name in ('name', 'world_position', 'rotation', 'scale', 'model', 'color', 'texture'):
                undo_data[name] = [getattr(icon.entity, name) for icon in self.editor_icons]

            undo_data['cursor_3d_position'] = self.cursor_3d.position

        self.undo_cache.append(undo_data)
        print('appened', undo_data)


    def load(self, name, folder=application.asset_folder / 'scenes'):
        t = time.time()
        for e in self.editor_icons:
            destroy(e)
        self.editor_icons.clear()
        scene_instance = None

        with open(folder / f'{name}.py') as f:
            try:
                exec(f.read())
                scene_instance = eval(f'Scene()')
                # entities = [e for e in scene.entities if e.has_ancestor(scene_instance)]
            except:
                print('error in scene:', name)

        # make icons
        for e in scene_instance.children:
            e.editor_icon = EditorIcon(parent=self.editor_icon_parent, scene_editor=self, entity=e)
            self.editor_icons.append(e.editor_icon)
            e.collision = False

        if scene_instance:
            print(f'loaded scene: "{name}" in {time.time()-t}')
            return scene_instance
        else:
            return False


    def set_attr_for_selected(self, name, value):
        # print('set:', name, value)
        for icon in self.selection:
            setattr(icon.entity, name, value)

        for menu in self.menus:
            menu.enabled = False


    def rename_selected(self, name=''):
        if not name:
            name = self.rename_window.content[0].text

        for icon in self.selection:
            icon.text = name
            icon.entity.name = name
            icon.text_entity.scale = 2

        self.rename_window.close()
        self.render_selection()


    def save(self):
        from save import save
        save(self)


    @property
    def show_names(self):
        return self._show_names

    @show_names.setter
    def show_names(self, value):
        self._show_names = value
        for icon in self.editor_icons:
            icon.text_entity.enabled = value


    def add_entity(self, name, position=Vec3(0,0,0), rotation=Vec3(0,0,0), scale=1, model='cube', color=color.light_gray, texture=''):
        e = Entity(name=name, position=position, rotation=rotation, scale=scale, model=model, color=color, texture=texture)
        e.editor_icon = EditorIcon(parent=self.editor_icon_parent, scene_editor=self, entity=e)
        e.editor_icon.text_entity.text = name
        self.editor_icons.append(e.editor_icon)
        return e


    def delete_entity(self, entity):
        self.editor_icons.remove(entity.editor_icon)
        destroy(entity.editor_icon)
        destroy(entity)


    def average_position_of_selection(self):
        _pos = Vec3(0,0,0)
        for icon in self.selection:
            _pos += icon.world_position
        _pos /= len(self.selection)
        return _pos


    def update(self):
        for icon in self.editor_icons:
            icon.position = icon.entity.world_position

        if self.rename_window.enabled:
            return

        if held_keys['control']:
            return

        if held_keys['x']:
            self.cursor_3d.x += sum(mouse.velocity) * 8
        if held_keys['y']:
            self.cursor_3d.y += sum(mouse.velocity) * 8
        if held_keys['z']:
            self.cursor_3d.z += sum(mouse.velocity) * 8

        if held_keys['s'] or held_keys['c']:  # scale from center
            _added_scale = sum(mouse.velocity) * 8
            self.cursor_3d.scale += Vec3(_added_scale, _added_scale, _added_scale)

        if held_keys['e'] + held_keys['s'] > 0:     # scale from individual origin
            for icon in self.selection:
                _added_scale = sum(mouse.velocity) * 8
                icon.entity.scale += Vec3(_added_scale, _added_scale, _added_scale)



    def input(self, key):
        if key == 'escape':
            self.rename_window.enabled = False

        if key == 'enter':
            if self.rename_window.enabled:
                self.rename_window.content[1].on_click()

        if self.rename_window.enabled:
            return

        if key == 'shift' or key == 'alt':
            for e in self.editor_icons:
                e.ignore = True

        if key == 'shift up' or key == 'alt up':
            for e in self.editor_icons:
                e.ignore = False


        if key in ('x', 'y', 'z', 's', 'e', 'c') and self.selection and not held_keys['control']:
            self.cursor_3d.visible = True
            self.cursor_3d.position = self.selection[-1].world_position

            if key == 'c':
                self.cursor_3d.position = self.average_position_of_selection()

            for icon in self.selection:
                icon.entity.original_parent = icon.entity.parent
                icon.entity._start_position = icon.entity.position
                icon.entity._start_scale = icon.entity.scale

                icon.entity.world_parent = self.cursor_3d

            if key in ('x', 'y', 'z') and not held_keys['control']:
                self.cursor_3d.rulers[('x', 'y', 'z').index(key)].enabled = True


        if key in ('x up', 'y up', 'z up', 's up', 'e up', 'c up') and not held_keys['control']:
            for icon in self.selection:
                icon.entity.world_parent = scene

            s = Sequence()
            s.extend([Func(setattr, icon.entity, 'position', icon.entity._start_position) for icon in self.selection])
            if key in ('s up', 'e up', 'c up'):
                s.extend([Func(setattr, icon.entity, 'scale', icon.entity._start_scale) for icon in self.selection])

            self.record_undo(s)

            self.cursor_3d.visible = False
            for ruler in self.cursor_3d.rulers:
                ruler.enabled = False


        if key == 'm':
            if self.model_menu.enabled:
                self.model_menu.enabled = False
                self.editor_camera.ignore = True
            elif self.selection:
                self.model_menu.enabled = True

        if key == 't' and not held_keys['shift']:
            if self.texture_menu.enabled:
                self.texture_menu.enabled = False
            elif self.selection:
                self.texture_menu.enabled = True
                self.editor_camera.ignore = True

        if held_keys['shift'] and key == 't':
            self.show_names = not self.show_names


        if key == 'h':
            self.editor_icon_parent.enabled = not self.editor_icon_parent.enabled

        if key == 'l':
            from ursina.shaders import basic_lighting_shader
            for icon in self.editor_icons:
                icon.entity.shader = basic_lighting_shader



        if key == 'n':
            e = self.add_entity('entity', position=self.average_position_of_selection())
            self.record_undo(Func(self.delete_entity, e))


        if held_keys['control'] and key == 'g':
            group = self.add_entity('group', model=None, position=self.average_position_of_selection())
            group.editor_icon.text_entity.enabled = True
            for icon in self.selection:
                icon.entity.world_parent = group

        if key == 'f2' and self.selection:
            self.rename_window.enabled = True
            self.rename_window.content[0].active = True
            self.rename_window.content[0].text = ''


        if key == '1':
            self.editor_camera.rotation = (0,0,0)
        if key == '7':
            self.editor_camera.rotation = (90,0,0)
        if key == '5':
            camera.orthographic = not camera.orthographic


        if key == 'left mouse down':
            if self.duplicate_dragger.enabled:
                return

            for key in ('x', 'y', 'z', 's', 'e', 'c'):
                if held_keys[key]:
                    return

            icon = mouse.hovered_entity
            if held_keys['shift'] + held_keys['alt'] == 0:

                menu_is_open = True in [e.enabled for e in self.menus]
                if not menu_is_open:
                    if not icon in self.selection:
                        self.clear_selection()
                    # elif self.selection and icon != self.selection[-1]:
                    #     self.clear_selection()

            if not icon in self.editor_icons:
                return

            if not icon in self.selection:
                self.selection.append(icon)
            else: # swap order
                print('swap')
                self.selection[-1], self.selection[self.selection.index(icon)] = self.selection[self.selection.index(icon)], self.selection[-1]

            if held_keys['alt'] and icon in self.editor_icons:
                # print('deselect')
                self.selection.remove(icon)

            self.render_selection()

        if held_keys['shift'] and key == 'd' and self.selection:
            self.duplicate_dragger.position = self.selection[-1].world_position

            for icon in self.selection:
                e = icon.entity
                clone = self.add_entity(name=icon.entity.name)
                # clone.original_parent = e.parent
                clone.world_position = e.world_position
                clone.world_scale = e.world_scale
                clone.world_rotation = e.world_rotation
                clone.model = copy(e.model)
                clone.texture = e.texture
                clone.color = e.color
                clone.world_parent = self.duplicate_dragger

            self.clear_selection()
            self.selection = [e.editor_icon for e in self.duplicate_dragger.children]
            self.render_selection()
            self.duplicate_dragger.enabled = True
            self.duplicate_dragger.start_dragging()



        if key == 'delete':
            if len(self.selection) == 1:
                icon = self.selection[0]
                self.record_undo(
                    Func(
                        self.add_entity,
                            name=icon.entity.name,
                            position=icon.entity.position, rotation=icon.entity.rotation, scale=icon.entity.scale,
                            model=icon.entity.model, color=icon.entity.color, texture=icon.entity.texture
                        )
                    )
            else:
                s = Sequence()
                for icon in self.selection:
                    s.append(
                        Func(
                            self.add_entity,
                                name=icon.entity.name,
                                position=icon.entity.position, rotation=icon.entity.rotation, scale=icon.entity.scale,
                                model=icon.entity.model, color=icon.entity.color, texture=icon.entity.texture
                            )
                        )
                # print('------------recorded undo', s)

            self.record_undo(s)

            for icon in self.selection:
                self.delete_entity(icon.entity)

            self.clear_selection()


        if held_keys['control'] and key == 's':
            self.save()


        if held_keys['control'] and key == 'z':
            data = self.undo_cache[self.undo_index]

            if isinstance(data, Sequence):
                print('----', data)
                data.start()

            if callable(data):
                print('----', data)
                data()

            self.undo_index -= 1
            # print(self.undo_index)
            self.undo_index = clamp(self.undo_index, 0, len(self.undo_cache)-1)
            # self.grid = deepcopy(self.undo_cache[self.undo_index])
            # for i, data in enumerate(self.undo_cache[self.undo_index]):
            if isinstance(data, dict):
                for i, icon in enumerate(self.editor_icons):
                    if i >= len(data['world_position']):
                        continue
                    for name in ('name', 'world_position', 'rotation', 'scale', 'model', 'color', 'texture'):
                        setattr(icon.entity, name, data[name][i])

                self.cursor_3d.position = data['cursor_3d_position']
                    # self.editor_icons[i].entity.world_position = pos

                # print('-------------', self.undo_index)
                # print([icon.entity.world_position for icon in self.editor_icons])


        # if held_keys['control'] and key == 'y':
        #     self.undo_index += 1
        #     self.undo_index = clamp(self.undo_index, 0, len(self.undo_cache)-1)
        #     self.grid = deepcopy(self.undo_cache[self.undo_index])
        #     self.render()


    def clear_selection(self):
        # print('clear selection')
        self.selection.clear()
        self.render_selection()
        self.model_menu.enabled = False


    def render_selection(self):
        for icon in self.editor_icons:
            # icon.sprite.color=color.white
            icon.color=color.white

        if self.selection:
            for icon in self.selection:
                # icon.sprite.color = color.azure
                icon.color = color.azure

            # self.selection[-1].sprite.color = color.cyan
            self.selection[-1].color = color.orange

        self.selection_text.text = 'Selection:\n' + '\n'.join([icon.entity.name for icon in self.selection])



if __name__ == '__main__':
    # window.vsync = False
    app = Ursina()
    SceneEditor()
    # from ursina.shaders import fxaa
    # camera.shader = fxaa
    # Sky()

    app.run()
