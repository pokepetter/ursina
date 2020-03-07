from ursina import *


class SceneEditor(Entity):
    def __init__(self, prefabs, **kwargs):
        super().__init__(parent=camera.ui, eternal=True,)

        Text.default_font = 'VeraMono.ttf'
        Text.size = .025 * .9

        self.editor_camera = EditorCamera(rotate_around_mouse_hit=False, enabled=False)
        self.ui_parent = Entity(parent=camera.ui)
        self.gizmo_parent = Entity()
        self.gizmo = Entity(parent=self.gizmo_parent, model=Cube(mode='line'), add_to_scene_entities=False)
        self.cursor = Entity(parent=self.gizmo, scale=.1, model='sphere', always_on_top=True, color=color.magenta)

        self.x_ruler = Entity(parent=self.gizmo_parent, model='cube', scale=(.025,.025,9999), color=color.magenta, enabled=False, rotation_y=90, add_to_scene_entities=False)
        self.y_ruler = Entity(parent=self.gizmo_parent, model='cube', scale=(.025,.025,9999), color=color.yellow, enabled=False, rotation_x=90, add_to_scene_entities=False)
        self.z_ruler = Entity(parent=self.gizmo_parent, model='cube', scale=(.025,.025,9999), color=color.cyan, enabled=False, add_to_scene_entities=False)
        self.world_plane = Entity(parent=self.gizmo_parent, model=Grid(64, 64), rotation_x=90, collider='box', origin=(.5,.5), scale=64, color=color.color(0,0,.5,.25), enabled=False)

        self.scene_folder = application.asset_folder / 'scenes'
        self.scene_menu_button = Button(parent=self.ui_parent, text='none', position=window.top_left + Vec2(.025+.0125,0), scale=(.25,.05), origin=(-.5,.5), on_click=self.toggle_scene_menu)
        self.scene_menu_button.text_entity.origin = (-.5,0)
        self.scene_menu_button.text_entity.position = (.05,-.5)
        self.scene_menu_button.down_arrow = Entity(parent=self.scene_menu_button.model, model='quad', texture='arrow_down', position=(.5-.05,0,-1), origin_x=.5, scale_y=.5)
        self.scene_menu_button.down_arrow.world_scale_x = self.scene_menu_button.down_arrow.world_scale_y
        self.scene_name = 'untitled_scene'
        self.scene_menu = ButtonList({}, parent=self.ui_parent, position=window.top_left - Vec2(0,.05), close_on_click_outside=True, enabled=False)
        self.ask_for_scene_name_window = WindowPanel(
            title='Enter scene name',
            content=(
                InputField(name='scene name'),
                Button(text='Save', color=color.azure, on_click=Func(self.save)),
            ),
            enabled=False,
            popup=True,
        )

        self.toolbar = Entity(parent=self.ui_parent, position=window.top_left + Vec2(.2, 0))
        self.tools = [
            SelectTool(parent=self),
            MoveTool(parent=self)
            ]
        self.tool = self.tools[0]

        self.hovered_entity = None
        self.hovered_entity_info = Text(parent=self.ui_parent, position=(0,-.45))
        self.selection = None
        self.clipboard = None

        self.edit_mode = False
        self.editor_toggle_button = Button(position=window.top_left, scale=(.025,.05), origin=(-.5,.5), color=color.orange)
        self.editor_toggle_button.icon = Entity(parent=self.editor_toggle_button, model='quad', texture='arrow_right', position=(.5,-.5), scale_y=.5)

        def toggle_edit_mode():
            self.edit_mode = not self.edit_mode
        self.editor_toggle_button.on_click = toggle_edit_mode

        self.entities = list()
        self.scene_file = None
        self.prefabs = prefabs
        self.prefab_menu = Entity(parent=self.ui_parent, enabled=False)
        self.prefab_menu.new_instance_target_position = Vec3(0,0,0)
        self.prefab_menu.bg = Button(
            parent=self.prefab_menu,
            model='quad',
            # collider='box',
            scale=(1000, 1000),
            z=1,
            color=color.clear,
            # highlight_color=color.black33,
            # pressed_color=color.black33,
            on_click=Func(setattr, self.prefab_menu, 'enabled', False)
            # on_click=Func(print, 'ffffffffffff')
            )

        for i, p in enumerate(self.prefabs):
            b = CreatePrefabButton(
                parent=self.prefab_menu,
                x=i*.1,
                scale=.1,
                scale_z=1,
                highlight_color=color.cyan,
                tooltip=Tooltip(p.__name__),
                scene_editor=self,
                class_to_instantiate=p
                )

            prefab = p(
                parent=b,
                rotation=(30,-30,0),
                scale=.5,
                ignore=True,
                collision=False,
                )


        self.color_menu = Panel(parent=self.ui_parent, model='quad', origin=(-.5,.5), scale=.5, color=color._32, enabled=False)
        self.color_menu.target_entity = None
        for i, (key, value) in enumerate(color.colors.items()):
            b = Button(parent=self.color_menu, scale=.1, z=-.1, color=value)
            b.on_click = f'self.parent.target_entity.color = color.{key}'

        grid_layout(self.color_menu.children, max_x=10, offset=(0,0,-.1))

        def color_menu_input(key):
            if (key == 'left mouse down' and mouse.hovered_entity is not None and not mouse.hovered_entity.has_ancestor(self.ui_parent)
            or key == 'escape'):
                self.color_menu.enabled = False
        self.color_menu.input = color_menu_input


        for key, value in kwargs.items():
            setattr(self, key, value)



    @property
    def edit_mode(self):
        return self._edit_mode

    @edit_mode.setter
    def edit_mode(self, value):
        self._edit_mode = value
        self.ui_parent.enabled = value
        self.editor_camera.enabled = value
        # self.world_plane.enabled = value
        self.gizmo.enabled = value
        self.editor_toggle_button.color = (color.orange, Button.color)[value]
        self.editor_toggle_button.icon.animate('rotation_z', self.editor_toggle_button.icon.rotation_z+180)
        self.toolbar.y += .05
        self.toolbar.animate('y', self.toolbar.y -.05, duration=.1, curve=curve.linear)

        if value == True:
            for e in self.entities:
                if e.model.name in ('quad', 'cube', 'plane'):
                    e.collider = 'box'
                else:
                    e.collider = 'mesh'

    @property
    def tools(self):
        return self._tools

    @tools.setter
    def tools(self, value):
        self._tools = value
        print('........', value)
        for child in self.toolbar.children:
            destroy(child)

        for i, e in enumerate(value):
            b = Button(
                parent=self.toolbar,
                model=Circle(),
                text=e.name[0],
                scale=Vec2(.05, .05) * .9,
                # origin=(-.5, .5),
                x=(i * .05) + .125,
                y=-.025,
                tool=e,
                tooltip=Tooltip(e.description),
                on_click=Func(setattr, self, 'tool', e)
                )
            # icon = Entity(parent=b, model='quad', texture='file_icon', origin=b.origin)



    @property
    def tool(self):
        return self._tool

    @tool.setter
    def tool(self, value):
        self._tool = value

        for e in self.tools:
            e.enabled = False
        value.enabled = True

        for b in self.toolbar.children:
            b.color = Button.color
            if b.tool == value:
                b.color = color.orange.tint(-.1)

    @property
    def scene_name(self):
        return self._scene_name

    @scene_name.setter
    def scene_name(self, value):
        self._scene_name = value
        self.scene_menu_button.text = value


    def toggle_scene_menu(self):
        self.scene_menu.enabled = not self.scene_menu.enabled
        if self.scene_menu.enabled:
            scenes_dict = dict()
            for e in self.scene_folder.iterdir():
                if e.is_file() and not '__' in e.stem:
                    scenes_dict[e.stem] = Func(self.load, e.stem)

            self.scene_menu.button_dict = scenes_dict


    def update(self):
        if not self.edit_mode:
            return

        if self.hovered_entity == mouse.hovered_entity:
            return

        if mouse.hovered_entity and mouse.hovered_entity in self.entities and not self.color_menu.enabled:
        #     self.hovered_entity_info.text = mouse.hovered_entity.name
            self.gizmo.enabled = True
            self.gizmo.world_position = mouse.hovered_entity.world_position
            self.gizmo.origin = mouse.hovered_entity.origin
            if mouse.hovered_entity.model:
                self.gizmo.scale = mouse.hovered_entity.bounds
            else:
                self.gizmo.scale = .1
        else:
        #     self.hovered_entity_info.text = 'None'
            self.gizmo.enabled = False
        #
        # self.x_ruler.enabled = False
        # self.y_ruler.enabled = False
        # self.z_ruler.enabled = False


        # if self.move_target:
            # mouse_velocity = (mouse.velocity[0] + mouse.velocity[1])
            # if held_keys['e'] or held_keys['s']:
            #     self.move_target.scale += Vec3(
            #         self.move_target.scale_x * mouse_velocity,
            #         self.move_target.scale_y * mouse_velocity,
            #         self.move_target.scale_z * mouse_velocity
            #         ) * 5
            #
            # if held_keys['r']:
            #     if not mouse.left:
            #         self.move_target.rotation_y -= mouse_velocity * 100
            #     else:
            #         print('r')
            #         self.move_target.rotation_x -= (mouse.velocity[1]) * 100
            #         self.move_target.rotation_z -= (mouse.velocity[0]) * 100
            #
            #
            # if self.tool == 'move_to_point':
            #     self.move_target.world_position = mouse.world_point
            #
            # if not held_keys['w']:
            #     self.x_ruler.enabled = held_keys['x']
            #     self.y_ruler.enabled = (held_keys['y'] + held_keys['c'])
            #     self.z_ruler.enabled = held_keys['z']
            #     self.x_ruler.position = self.move_target.position
            #     self.y_ruler.position = self.move_target.position
            #     self.z_ruler.position = self.move_target.position
            #     self.move_target.world_x += mouse_velocity * 10 * held_keys['x']
            #     self.move_target.world_y += mouse_velocity * 10 * (held_keys['y'] + held_keys['c'])
            #     self.move_target.world_z += mouse_velocity * 10 * held_keys['z']



    def input(self, key):
        key = ''.join((e+'+' for e in ('control', 'shift', 'alt') if held_keys[e] and not e == key)).replace('control', 'ctrl') + key

        if key == 'tab':
            self.edit_mode = not self.edit_mode

        if not self.edit_mode:
            return




        # if key == 'left mouse down' and mouse.hovered_entity in self.entities and not self.move_target and not self.color_menu.enabled:   # place new prefab instance
        #     elif self.tool == 'move_to_point':
        #         self.move_target.collision = False
        #
        #     # undo_cache.append(Func(setattr, self.move_target, 'world_position', self.move_target.original_position))


        if key == 'ctrl+s':
            self.save()
            return


        for e in self.tools:
            if hasattr(e, 'hotkeys') and key in e.hotkeys:
                print('.-----', e)
                self.tool = e

        if key == 'n' or key == 'right mouse up' and abs(sum(mouse.delta_drag)) < .01:
            self.world_plane.enabled = True
            self.prefab_menu.new_instance_target_position = mouse.world_point
            self.prefab_menu.enabled = True
            self.prefab_menu.position = mouse.position + Vec3(.05,.05,0)

        if key == 'b' and mouse.hovered_entity in self.entities:
            self.color_menu.target_entity = mouse.hovered_entity
            print('----', self.color_menu.target_entity)
            self.color_menu.enabled = True
            self.color_menu.position = mouse.position + Vec3(.05,.05,0)


        if key == 'm' and mouse.hovered_entity in self.entities:
            print('open model menu for:', mouse.hovered_entity.name)


        if key == 'ctrl+d' and mouse.hovered_entity in self.entities: # duplicate
            instance = duplicate(mouse.hovered_entity)
            self.entities.append(instance)
            self.tool = 'move_to_point'
            self.input('left mouse down')
            # self.move_target = instance


    def save(self, save_new=False):
        if self.scene_name == 'untitled' and not self.ask_for_scene_name_window.enabled or save_new:
            self.ask_for_scene_name_window.enabled = True
            self.ask_for_scene_name_window.content[0].active = True
            # self.ask_for_scene_name_window.content[1].on_click = Func(self.save)

        if self.ask_for_scene_name_window.enabled:
            if self.ask_for_scene_name_window.content[0].text == '':
                print('please enter a scene name')
                return False
            if ' ' in self.ask_for_scene_name_window.content[0].text:
                print('spaces not allowed')
                return False

            self.scene_name = self.ask_for_scene_name_window.content[0].text
            self.ask_for_scene_name_window.content[0].text = ''
            self.ask_for_scene_name_window.enabled = False

        print('saving:', self.scene_name)
        self.scene_folder.mkdir(parents=True, exist_ok=True)
        # create __init__ file in scene folder so we can import it during self.load()
        if not Path(self.scene_folder / '__init__.py').is_file():
            with open(self.scene_folder / '__init__.py', 'w', encoding='utf-8') as f:
                pass

        scene_file_content = dedent(f'''
            class Scene(Entity):
                def __init__(self, **kwargs):
                    super().__init__(**kwargs)
        ''')
        temp_entity= Entity()
        attrs_to_save = ('position', 'rotation', 'scale', 'model', 'origin', 'color', 'texture')

        for e in self.entities:
            scene_file_content += '        ' + e.__class__.__name__ + '(parent=self'

            for i, name in enumerate(attrs_to_save):
                if not getattr(e, name) == getattr(temp_entity, name):
                    if name == 'model':
                        model_name = e.model.name
                        scene_file_content += f", model='{model_name}'"
                        continue
                    if name == 'color':
                        alpha = f',{e.color.a}' if e.color.a < 1 else ''
                        scene_file_content += f', color=color.hsv({e.color.h},{e.color.s},{e.color.v}{alpha})'.replace('.0,', ',').replace('.0)',')')
                        continue

                    value = getattr(e, name)
                    if isinstance(value, Vec3):
                        value = str(round(value)).replace(' ', '')
                    scene_file_content += f", {name}={value}"

            scene_file_content += ')\n'

        print('scene_file_content:\n', scene_file_content)
        with open(f'{self.scene_folder/self.scene_name}.py', 'w', encoding='utf-8') as f:
            f.write(scene_file_content)


    def load(self, name):
        for e in self.entities:
            destroy(e)
        self.entities.clear()

        with open(self.scene_folder / f'{name}.py') as f:
            try:
                exec(f.read())
                instance = eval(f'Scene()')
                self.entities = instance.children
                self.scene_name = name
                self.edit_mode = True
                return instance
            except:
                print('error in scene:', name)


class MoveTool(Entity):
    def __init__(self, parent, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.name = 'move tool'
        self.description = 'move_x_z'
        self.target = None
        self.offset = Vec3(0,0,0)
        self.hotkeys = ['w', ]


    def input(self, key):
        if key == 'left mouse down' and mouse.hovered_entity:
            self.target = mouse.hovered_entity

            self.parent.world_plane.enabled = True
            self.parent.world_plane.rotation = (90,0,0)
            self.parent.world_plane.y = mouse.hovered_entity.world_y
            for e in self.parent.entities:
                e.collision = False

            if not self.offset:
                self.offset = self.target.world_position - Vec3(mouse.world_point[0], self.target.y, mouse.world_point[2])

        if key == 'left mouse up' and self.target:
            for e in self.parent.entities:
                e.collision = True

            # undo_cache.append(Func(setattr, self.move_target, 'world_position', self.move_target.original_position))
            self.target = None
            self.parent.world_plane.enabled = False
            self.offset = Vec3(0,0,0)


    def update(self):
        if not self.target:
            return
        # if self.tool == 'move_x_z':

        self.target.world_position = Vec3(mouse.world_point[0], self.target.y, mouse.world_point[2]) + self.offset
        if held_keys['control']:
            self.target.world_position = round(self.target.world_position, 1)


class SelectTool(Entity):
    def __init__(self, parent, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.name = 'select tool'
        self.description = 'SelectTool'
        self.hotkeys = ['q', ]

    def input(self, key):
        if key == 'left mouse down':
            if not mouse.hovered_entity:
                self.parent.selection = []
            elif not held_keys['control']:
                self.parent.selection = [mouse.hovered_entity, ]
            else:
                self.parent.selection.append(mouse.hovered_entity)




class CreatePrefabButton(Button):
    def on_click(self):
        instance = self.class_to_instantiate()
        self.scene_editor.prefab_menu.enabled = False
        # self.scene_editor.move_target.collision = False
        self.scene_editor.entities.append(instance)
        instance.position = self.scene_editor.prefab_menu.new_instance_target_position

        if not instance.model:
            instance.model = 'cube'

        if instance.model and instance.model.name in ('quad', 'cube', 'plane'):
            instance.collider = 'box'
        else:
            instance.collider = 'mesh'

        print('--------- added entity')


if __name__ == '__main__':
    # window.vsync = False
    app = Ursina()
    # create scene
    from ursina.prefabs.primitives import *

    player = OrangeCube(scale_y=2, origin_y=-.5, x=1)
    # FirstPersonController()
    # def player_update():
    #     player.x += held_keys['d'] * time.dt
    #     player.x -= held_keys['a'] * time.dt
    # player.update = player_update


    scene_editor = SceneEditor(prefabs=[Entity, RedCube, PinkCube, LimeCube])
    scene_editor.entities = [
        RedCube(z=4),
        GreenPlane(scale=16),
        player
        ]

    Sky()


    app.run()
