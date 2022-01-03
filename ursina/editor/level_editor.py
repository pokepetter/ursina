from ursina import *
from ursina.shaders import lit_with_shadows_shader, unlit_shader
from time import perf_counter


class Scene(Entity):
    def __init__(self, x, y, name, **kwargs):
        super().__init__()
        self.coordinates = [x,y]
        self.name = name
        self.path = None    # must be assigned to be able to load
        self.entities = []
        self.selection = []
        self.scene_parent = None
        # self.undo_handler     # gets assigned later

    def save(self):
        if not self.path and not self.entities:
            print('cant save scene with not path and no entities')
            return

        level_editor.scene_folder.mkdir(parents=True, exist_ok=True)
        # create __init__ file in scene folder so we can import it during self.load()
        if not Path(level_editor.scene_folder / '__init__.py').is_file():
            print('creating an __init__.py in the scene folder')
            with open(level_editor.scene_folder / '__init__.py', 'w', encoding='utf-8') as f:
                pass

        print('saving:', self.name)
        scene_file_content = dedent(
            '\x1f            class Scene(Entity):\x1f                def __init__(self, **kwargs):\x1f                    super().__init__(**kwargs)\x1f        '
        )


        for e in self.entities:
            if hasattr(e, 'is_gizmo'):
                continue

            scene_file_content += '        '
            if e.name != camel_to_snake(e.__class__.__name__):
                scene_file_content += f'self.{camel_to_snake(e.__class__.__name__)} = '

            scene_file_content += f'{e.__class__.__name__}(parent=self, '

            if hasattr(e, '__repr__'):
                recipe = repr(e).split(e.__class__.__name__)[1][1:-1] # remove start and end
                # if 'parent=' in recipe: # remove parent
                #     beginning, end = recipe.split('parent=')
                #     print('---------', beginning, end)
                #     recipe = beginning + end.split(',',1)[1]

                scene_file_content += recipe
                scene_file_content += ')\n' # TODO: add if it has a custom name

        # print('scene_file_content:\n', scene_file_content)
        self.path = level_editor.scene_folder/(self.name+'.py')
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(scene_file_content)
        print('saved:', self.path)


    def load(self):
        # print('aaaaaaaaa')
        if not self.path:
            print('cant load scene, no path')
            return
        if self.scene_parent:
            print('error, scene already loaded')
            return

        t = perf_counter()
        with open(self.path) as f:
            try:
                entities_before_exec = list(scene.entities)
                exec(f.read())
                self.scene_parent = eval('Scene()')
                self.scene_parent.name = self.name
                self.entities = [e for e in scene.entities if e.has_ancestor(self.scene_parent) and not hasattr(e, 'is_gizmo')]
                for e in self.entities:
                    # e.collider = 'box'
                    # e.collision = False
                    e.shader = lit_with_shadows_shader
                    # e.ignore = True
                    e.selectable = True
                    e.original_parent = e.parent
                    if e.model.name == 'cube':
                        e.collider = 'box'
                        e.collision = False


            except Exception as e:
                print('error in scene:', self.name, e)
                [destroy(e) for e in scene.entities if e not in entities_before_exec]

        if self.scene_parent:
            print(f'loaded scene: "{self.name}" in {perf_counter()-t}')
            return self.scene_parent


    def unload(self):
        [setattr(e, 'parent', level_editor) for e in level_editor.cubes]
        [destroy(e) for e in self.entities]
        # if not self.scene_parent:
        #     # print('cant unload scene, its already empty')
        #     return

        self.selection = []
        self.entities = []
        destroy(self.scene_parent)


class LevelEditor(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.scene_folder = application.asset_folder / 'scenes'
        self.scenes = [[Scene(x, y, f'untitled_scene[{x},{y}]') for y in range(8)] for x in range(8)]
        self.current_scene = None

        self.grid = Entity(parent=self, model=Grid(16,16), rotation_x=90, scale=64, collider='box', color=color.white33, enabled=False)
        self.origin_mode = 'center'
        self.editor_camera = EditorCamera(parent=self, rotation_x=20, eternal=False)
        self.ui = Entity(parent=camera.ui, name='level_editor.ui')

        self.point_renderer = Entity(parent=self, model=Mesh([], mode='point', thickness=.20, render_points_in_3d=True), texture='circle', always_on_top=True, unlit=True, render_queue=1)
        self.cubes = [Entity(model='wireframe_cube', color=color.azure, parent=self, enabled=False) for i in range(32)]

        self.origin_mode_menu = ButtonGroup(['last', 'center', 'individual'], min_selection=1, position=window.top, parent=self.ui)
        self.origin_mode_menu.scale *= .75
        self.origin_mode_menu.on_value_changed = self.render_selection
        self.local_global_menu = ButtonGroup(['local', 'global'], min_selection=1, position=window.top - Vec2(.2,0), parent=self.ui)
        self.local_global_menu.scale *= .75
        self.local_global_menu.on_value_changed = self.render_selection
        # self.current_poke_node = None
        self.entity_list_text = Text(parent=self.ui, scale=.5, position=window.left)

    @property
    def entities(self):
        if not self.current_scene:
            return []
        return self.current_scene.entities

    @property
    def selection(self):
        if not self.current_scene:
            return []
        return self.current_scene.selection

    @selection.setter
    def selection(self, value):
        self.current_scene.selection = value


    def input(self, key):
        if held_keys['control'] and not held_keys['shift'] and not held_keys['alt'] and key == 's':
            if not self.current_scene:
                print("no current_scene, can't save")
                return

            self.current_scene.save()


    def render_selection(self, update_gizmo_position=True):
        # entities = self.entities
        # if self.current_poke_node:
        #     selectable_entities = self.current_poke_node.point_gizmos
        # for e in self.entities:
        #     print(e, e.selectable)

        # self.entity_list_text.text = '\n'.join(([f'{('', '<azure>')[int(e in self.selection)]}{e.name}    {e.selectable}<default>' for e in self.entities])
        text = ''
        for e in self.entities:
            text += '<azure>' if e in self.selection else '<default>'
            text += f'{e.name}\n' if e else 'ERROR: \n'
        self.entity_list_text.text = text

        for i, e in enumerate(self.entities):
            if e is None:
                print(f'error in entities {i}, is {e}')
                self.entities.remove(e)


        self.point_renderer.model.vertices = [e.world_position for e in self.entities if e.selectable and not e.collider]
        self.point_renderer.model.colors = [color.azure if e in self.selection else color.yellow for e in self.entities if e.selectable and not e.collider]
        self.point_renderer.model.generate()

        gizmo.enabled = bool(self.selection)

        if update_gizmo_position and self.selection:
            if self.origin_mode_menu.value in ('last', 'individual'):
                gizmo.world_position = self.selection[-1].world_position
            elif self.origin_mode_menu.value == 'center':
                gizmo.world_position = sum(
                    e.world_position for e in self.selection
                ) / len(self.selection)


            if self.local_global_menu.value == 'local' and self.origin_mode_menu.value == 'last':
                gizmo.world_rotation = self.selection[-1].world_rotation
            else:
                gizmo.world_rotation = Vec3(0,0,0)

        [e.disable() for e in self.cubes]
        # [setattr(e, 'parent', self) for e in self.cubes]
        for i, e in enumerate(e for e in self.selection if e.collider):
            if i < len(self.cubes):
                self.cubes[i].world_transform = e.world_transform

                # self.cubes[i].parent = e
                self.cubes[i].enabled = True


        # print('---------- rendered selection')
    def on_enable(self):
        if hasattr(self, 'ui'):
            self.ui.enabled = True

    def on_disable(self):
        self.ui.enabled = False




class Undo(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=level_editor, undo_data=[], undo_index=-1)

    def record_undo(self, data):
        print('record undo:', data)
        self.undo_data = self.undo_data[:self.undo_index+1]
        self.undo_data.append(data)
        self.undo_index += 1

    def undo(self):
        if self.undo_index < 0:
            return

        current_undo_data = self.undo_data[self.undo_index]

        if current_undo_data[0] == 'restore entities':     # restore deleted entity
            for id, recipe in zip(current_undo_data[1], current_undo_data[2]):
                # print('------------', recipe)
                clone = eval(recipe)
                clone.selectable = True
                clone.original_parent = clone.parent
                clone.shader = lit_with_shadows_shader
                # print('------------', recipe, id, 'clone:', clone)
                level_editor.entities.insert(id, clone)

        elif current_undo_data[0] == 'delete entities': # delete newly created entity
            target_entities = [level_editor.entities[id] for id in current_undo_data[1]]
            [level_editor.selection.remove(e) for e in target_entities if e in level_editor.selection]
            [setattr(e, 'parent', level_editor) for e in level_editor.cubes]
            [level_editor.entities.remove(e) for e in target_entities]
            [destroy(e) for e in target_entities]

        else:
            for data in current_undo_data:
                id, attr, original, new = data
                setattr(level_editor.entities[id], attr, original)

        level_editor.render_selection()     # make sure the gizmo position updates
        self.undo_index -= 1

    def redo(self):
        if self.undo_index+2 > len(self.undo_data):
            return

        current_undo_data = self.undo_data[self.undo_index+1]

        # do the same as for undo, but opposite
        if current_undo_data[0] == 'delete entities':     # delete entity
            # pass
            for id, recipe in zip(current_undo_data[1], current_undo_data[2]):
                clone = eval(recipe)
                clone.selectable = True
                clone.original_parent = clone.parent
                clone.shader = lit_with_shadows_shader
                level_editor.entities.insert(id, clone)

        elif current_undo_data[0] == 'restore entities': # restore entity
            target_entities = [level_editor.entities[id] for id in current_undo_data[1]]
            [level_editor.selection.remove(e) for e in target_entities if e in level_editor.selection]
            [setattr(e, 'parent', level_editor) for e in level_editor.cubes]
            [level_editor.entities.remove(e) for e in target_entities]
            [destroy(e) for e in target_entities]


        else:
            for data in current_undo_data:
                id, attr, original, new = data
                setattr(level_editor.entities[id], attr, new)

        level_editor.render_selection()     # make sure the gizmo position updates
        self.undo_index += 1

    def input(self, key):
        if held_keys['control']:
            if key == 'z':
                self.undo()
            elif key == 'y':
                self.redo()




axis_colors = {
    'x' : color.magenta,
    'y' : color.yellow,
    'z' : color.cyan
}

# if not load_model('arrow'):
#     p = Entity(enabled=False)
#     Entity(parent=p, model='cube', scale=(1,.05,.05))
#     Entity(parent=p, model=Cone(4, direction=(1,0,0)), x=.5, scale=.2)
#     arrow_model = p.combine()
#     arrow_model.save('arrow.ursinamesh', path=internal_models_compressed_folder)
#
# if not load_model('scale_gizmo'):
#     p = Entity(enabled=False)
#     Entity(parent=p, model='cube', scale=(.05,.05,1))
#     Entity(parent=p, model='cube', z=.5, scale=.2)
#     arrow_model = p.combine()
#     arrow_model.save('scale_gizmo.ursinamesh', path=internal_models_compressed_folder)


class GizmoArrow(Draggable):
    def __init__(self, model='arrow', collider='box', **kwargs):
        super().__init__(model=model, origin_x=-.55, always_on_top=True, render_queue=1, is_gizmo=True, shader=unlit_shader, **kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.record_undo = True     # this can be set to False when moving this though code for example, and you don't want it to record undo.
        self.original_rotation = self.rotation


    def drag(self):
        self.world_parent = level_editor
        self.gizmo.world_parent = self
        for e in level_editor.selection:
            if level_editor.local_global_menu.value == 'global':
                e.world_parent = self
            else:
                e.world_parent = self.gizmo.fake_gizmo

            e.always_on_top = False
            e._original_world_transform = e.world_transform

    def drop(self):
        self.gizmo.world_parent = level_editor
        if self.record_undo:
            changes = []
            for e in level_editor.selection:
                e.world_parent = e.original_parent
                changes.append([level_editor.entities.index(e), 'world_transform', e._original_world_transform, e.world_transform])

            level_editor.current_scene.undo.record_undo(changes)

        self.parent = self.gizmo.arrow_parent
        self.position = (0,0,0)
        self.rotation = self.original_rotation
        level_editor.render_selection()



class Gizmo(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=level_editor, enabled=False)
        self.arrow_parent = Entity(parent=self)
        self.lock_axis_helper_parent = Entity(parent=level_editor,
            # model='wireframe_cube',
        )
        self.lock_axis_helper = Entity(parent=self.lock_axis_helper_parent,
            # model=Circle(6, radius=.2), color=color.red, double_sided=True, always_on_top=True, render_queue=1
        ) # this will help us lock the movement to an axis on local space


        self.subgizmos = {
            'xz' : GizmoArrow(parent=self.arrow_parent, gizmo=self, model='cube', scale=.6, scale_y=.05, origin=(-.75,0,-.75), color=lerp(color.magenta, color.cyan, .5), plane_direction=(0,1,0)),
            'x'  : GizmoArrow(parent=self.arrow_parent, gizmo=self, color=axis_colors['x'], lock=(0,1,1)),
            'y'  : GizmoArrow(parent=self.arrow_parent, gizmo=self, rotation=(0,0,-90), color=axis_colors['y'], lock=(1,0,1)),
            'z'  : GizmoArrow(parent=self.arrow_parent, gizmo=self, rotation=(0,-90,0), color=axis_colors['z'], plane_direction=(0,1,0), lock=(1,1,0)),
        }
        for e in self.arrow_parent.children:
            e.highlight_color = color.white
            e.original_scale = e.scale

        self.fake_gizmo = Entity(parent=level_editor, enabled=False)
        self.fake_gizmo.subgizmos = {}
        for key, value in self.subgizmos.items():
            self.fake_gizmo.subgizmos[key] = duplicate(self.subgizmos[key], parent=self.fake_gizmo, collider=None, ignore=True)


    def input(self, key):   # this will execute before GizmoArrow drag()
        if key == 'left mouse down' and mouse.hovered_entity in self.subgizmos.values():
            self.drag()

        if key == 'left mouse up' and level_editor.local_global_menu.value == 'local':
            self.drop()


    def drag(self, show_gizmo_while_dragging=True):
        for i, axis in enumerate('xyz'):
            self.subgizmos[axis].plane_direction = self.up

            self.subgizmos[axis].lock = [0,0,0]
            if level_editor.local_global_menu.value == 'global':
                self.subgizmos[axis].lock = [1,1,1]
                self.subgizmos[axis].lock[i] = 0

            if axis == 'y':
                self.subgizmos[axis].plane_direction = self.forward

        self.subgizmos['xz'].plane_direction = self.up

        # use fake gizmo technique to lock movement to local axis. if in global mode, skip this and use the old simpler way.
        if level_editor.local_global_menu.value == 'local':
            self.lock_axis_helper_parent.world_transform = self.world_transform
            self.lock_axis_helper.position = (0,0,0)
            self.fake_gizmo.world_transform = self.world_transform

            self.fake_gizmo.enabled = True
            self.visible = False
            if show_gizmo_while_dragging:
                [setattr(e, 'visible_self', True) for e in self.fake_gizmo.subgizmos.values()]
            [setattr(e, 'visible_self', False) for e in self.subgizmos.values()]


    def drop(self):
        self.fake_gizmo.enabled = False
        self.visible = True
        [setattr(e, 'visible_self', False) for e in self.fake_gizmo.subgizmos.values()]
        [setattr(e, 'visible_self', True) for e in self.subgizmos.values()]
        [setattr(e, 'scale', e.original_scale) for e in self.subgizmos.values()]


    def update(self):
        self.world_scale = distance(self.world_position, camera.world_position) * .025

        for i, axis in enumerate('xyz'):
            if self.subgizmos[axis].dragging:
                setattr(self.lock_axis_helper, axis, self.subgizmos[axis].get_position(relative_to=self.lock_axis_helper_parent)[i])
                self.fake_gizmo.world_position = self.lock_axis_helper.world_position

        if self.subgizmos['xz'].dragging:
            self.fake_gizmo.world_position = self.subgizmos['xz'].world_position


class RotationGizmo(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=gizmo)

        self.rotator = Entity(parent=gizmo)
        self.axis = Vec3(0,1,0)
        self.subgizmos = {}
        self.sensitivity = 36000
        self.dragging = False

        path = Circle(24).vertices
        path.append(path[0])
        rotation_gizmo_model = Pipe(base_shape=Quad(radius=0), path=[Vec3(e)*32 for e in path])

        for i, dir in enumerate((Vec3(-1,0,0), Vec3(0,1,0), Vec3(0,0,-1))):
            b = Button(parent=self, model=copy(rotation_gizmo_model), collider='mesh',
                color=axis_colors[('x','y','z')[i]], is_gizmo=True, always_on_top=True, render_queue=1, unlit=True, double_sided=True,
                on_click=Sequence(Func(setattr, self, 'axis', dir), Func(self.drag)),
                drop=self.drop,
                name=f'rotation_gizmo_{"xyz"[i]}',
                scale=1/32
                )
            b.look_at(dir)
            b.original_color = b.color
            b.start_dragging = b.on_click   # for the quick rotate
            b.on_mouse_enter = Func(setattr, b, 'color', color.white)
            b.on_mouse_exit = Func(setattr, b, 'color', b.original_color)

            self.subgizmos['xyz'[i]] = b


    def drag(self):
        self.rotator.world_parent = scene
        print('drag')
        for e in level_editor.selection:
            e.world_parent = self.rotator
            e._original_world_transform = e.world_transform
        self.dragging = True

    def drop(self):
        print('drop')
        self.rotator.world_parent = gizmo
        changes = []
        for e in level_editor.selection:
            e.world_parent = e.original_parent
            changes.append([level_editor.entities.index(e), 'world_transform', e._original_world_transform, e.world_transform])

        level_editor.current_scene.undo.record_undo(changes)
        self.dragging = False
        self.rotator.rotation = (0,0,0)
        level_editor.render_selection()

    def input(self, key):
        if key == 'left mouse up' and self.dragging:
            self.dragging = False
            self.drop()


    def update(self):
        if self.dragging:
            rotation_amount = Vec3(sum(mouse.velocity), sum(mouse.velocity), sum(mouse.velocity)) * self.sensitivity * time.dt * self.axis * Vec3(1,1,-1)
            if level_editor.origin_mode_menu.value != 'individual':
                self.rotator.rotation -= rotation_amount
            else:
                for e in level_editor.selection:
                    e.rotation -= rotation_amount




class ScaleGizmo(Draggable):
    def __init__(self, **kwargs):
        super().__init__(parent=gizmo, model='cube', scale=.25, color=color.orange, visible=True, always_on_top=True, render_queue=1, is_gizmo=True, dragging=False, shader=unlit_shader)
        self.scaler = Entity(parent=gizmo)
        self.axis = Vec3(1,1,1)
        self.on_click = Func(setattr, self, 'axis', Vec3(1,1,1))
        self.subgizmos = {}
        self.sensitivity = 300

        for i, dir in enumerate((Vec3(1,0,0), Vec3(0,1,0), Vec3(0,0,1))):
            b = Button(parent=self, model='scale_gizmo', origin_z=-.5, scale=4, collider='box',
                color=axis_colors[('x','y','z')[i]], is_gizmo=True, always_on_top=True, render_queue=1, shader=unlit_shader,
                on_click=Sequence(Func(setattr, self, 'axis', dir), Func(self.drag)), name=f'scale_gizmo_{"xyz"[i]}')
            b.look_at(dir)
            self.subgizmos['xyz'[i]] = b


    def drag(self):
        for e in level_editor.selection:
            e.world_parent = self.scaler
            e._original_world_transform = e.world_transform
        self.dragging = True

    def drop(self):
        changes = []
        for e in level_editor.selection:
            e.world_parent = e.original_parent
            changes.append([level_editor.entities.index(e), 'world_transform', e._original_world_transform, e.world_transform])

        level_editor.current_scene.undo.record_undo(changes)
        self.dragging = False
        self.scaler.scale = 1
        level_editor.render_selection()



    def update(self):
        if self.dragging:
            if level_editor.origin_mode_menu.value != 'individual':
                self.scaler.scale += Vec3(sum(mouse.velocity), sum(mouse.velocity), sum(mouse.velocity)) * self.sensitivity * time.dt * self.axis
            else:
                for e in level_editor.selection:
                    e.scale += Vec3(sum(mouse.velocity), sum(mouse.velocity), sum(mouse.velocity)) * self.sensitivity * time.dt * self.axis

class BoxGizmo(Entity):
    def __init__(self):
        super().__init__(parent=level_editor)
        self.target = None
        self.scaler = Entity(parent=self)
        self.helper = Entity(parent=self, model='cube', unlit=True, color=color.azure, enabled=False)
        self.sensitivity = 600
        self.scale_from_center = False    # scale from center if holding alt
        self.normal = None
        self.axis_name = None

    def input(self, key):
        if key == 't':
            [setattr(e, 'collision', True) for e in level_editor.entities]
            mouse.update()
            if mouse.hovered_entity in level_editor.entities and mouse.normal and mouse.normal != Vec3(0):
                self.target = mouse.hovered_entity
                self.target.original_parent = self.target.parent

                self.normal = Vec3(mouse.normal)
                self.axis_name = 'xyz'[[abs(int(e)) for e in self.normal].index(1)]

                self.scale_from_center = held_keys['alt']
                if not self.scale_from_center:
                    self.scaler.parent = self.target
                    self.scaler.position = -self.normal * .5
                    self.scaler.rotation = Vec3(0)
                    self.scaler.world_parent = self
                else:
                    self.scaler.position = self.target.world_position
                    self.scaler.rotation = self.target.world_rotation

                self.target.world_parent = self.scaler

                self.helper.parent = self
                self.helper.parent = self.target
                self.helper.position = self.normal / 2
                self.helper.rotation = Vec3(0)

                self.helper.world_scale = .05

                level_editor.local_global_menu.original_value = level_editor.local_global_menu.value
                if level_editor.local_global_menu.value != 'local':
                    level_editor.local_global_menu.value = 'local'

                level_editor.selection = [self.helper, ]
                level_editor.render_selection()
                gizmo.enabled = True
                gizmo.drag(show_gizmo_while_dragging=False)
                gizmo.subgizmos[self.axis_name].start_dragging()


        elif key == 't up' and self.target:
            [setattr(e, 'collision', False) for e in level_editor.entities]
            self.target.world_parent = self.target.original_parent
            self.target = None
            self.normal = None
            self.scaler.scale = 1
            self.helper.parent = self

            gizmo.drop()
            gizmo.subgizmos[self.axis_name].record_undo = False
            gizmo.subgizmos[self.axis_name].stop_dragging()
            gizmo.subgizmos[self.axis_name].record_undo = True
            level_editor.selection = []
            level_editor.local_global_menu.value = level_editor.local_global_menu.original_value
            gizmo.enabled = False
            self.helper.enabled = False

    def update(self):
        if self.target and held_keys['t']:
            relative_position = self.helper.get_position(relative_to=self.scaler)
            value = abs(relative_position[[abs(int(e)) for e in self.normal].index(1)])
            if self.scale_from_center:
                value *= 2

            setattr(self.target, f'scale_{self.axis_name}', value)

            if not self.scale_from_center:
                self.target.world_position = lerp(self.scaler.world_position, self.helper.world_position, .5)




class GizmoToggler(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.animator = Animator({
            'w' : gizmo.arrow_parent,
            'e' : scale_gizmo,
            'r' : rotation_gizmo,
            # 't' : box_gizmo,

            'q' : None,
        })

    def input(self, key):
        if key in self.animator.animations:
            self.animator.state = key


class QuickGrabber(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.target_entity = None
        self.target_axis = None
        self.target_gizmo = None


    def input(self, key):
        if held_keys['control'] or held_keys['shift'] or held_keys['alt']:
            return

        if key in ('x', 'y', 'z', 'g'):
            self.target_entity = selector.get_hovered_entity()

            if self.target_entity:
                print(self.target_entity.color)
                self.target_axis = key
                if key == 'g':
                    self.target_axis = 'xz'

                level_editor.selection = [self.target_entity, ]
                level_editor.render_selection()

                level_editor.local_global_menu.orignal_value = level_editor.local_global_menu.value
                level_editor.local_global_menu.orignal_value = 'global'

                gizmo.drag(show_gizmo_while_dragging=False)
                self.target_gizmo = gizmo.subgizmos[self.target_axis]
                self.target_gizmo.start_dragging()

        elif key in ('x up', 'y up', 'z up', 'g up') and self.target_entity:
            self.target_entity = None
            gizmo.drop()
            self.target_gizmo.stop_dragging()
            level_editor.selection = []
            level_editor.render_selection()




class QuickScaleOrRotate(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=level_editor,
            gizmos_to_toggle={
                's' : scale_gizmo,
                'sx' : scale_gizmo,
                'sy' : scale_gizmo,
                'sz' : scale_gizmo,
                'c' : rotation_gizmo.subgizmos['y'],
            },
            clear_selection = False
            )


    def input(self, key):
        if held_keys['control'] or held_keys['shift'] or held_keys['alt']:
            return

        if held_keys['s'] and key != 's':
            key = 's' + key

        if key in ('c',):
            self.original_gizmo_state = gizmo_toggler.animator.state
            gizmo_toggler.animator.state = 'r'

        elif key in ('s', 'sx', 'sy', 'sz'):
            self.original_gizmo_state = gizmo_toggler.animator.state
            gizmo_toggler.animator.state = 'e'

            if key != 's':
                scale_gizmo.axis = (Vec3(1,0,0), Vec3(0,1,0), Vec3(0,0,1))[('sx', 'sy', 'sz').index(key)]


        if key in self.gizmos_to_toggle.keys():
            selector.enabled = False
            selection_box.enabled = False

            gizmo.arrow_parent.visible = False
            scale_gizmo.visible = False
            self.gizmos_to_toggle[key].visible_self = False
            if key not in ('sx', 'sy', 'sz'):
                self.clear_selection = not level_editor.selection

            if not level_editor.selection:
                selector.input('left mouse down')

            invoke(self.gizmos_to_toggle[key].input, 'left mouse down', delay=1/60)
            invoke(self.gizmos_to_toggle[key].start_dragging, delay=1/60)


        if key.endswith(' up') and key[:-3] in self.gizmos_to_toggle.keys():
            key = key[:-3]
            self.gizmos_to_toggle[key].input('left mouse up')
            self.gizmos_to_toggle[key].drop()
            if self.clear_selection:
                level_editor.selection.clear()
                level_editor.render_selection()

            gizmo.arrow_parent.visible = True
            scale_gizmo.visible = True
            scale_gizmo.axis = Vec3(1,1,1)
            self.gizmos_to_toggle[key].visible_self = True
            gizmo_toggler.animator.state = self.original_gizmo_state

            selector.enabled = True
            selection_box.enabled = True


    def update(self):
        for key in self.gizmos_to_toggle.keys():
            if held_keys[key] and not held_keys['control'] and not held_keys['shift'] and mouse.velocity != Vec3(0,0,0):
                level_editor.render_selection(update_gizmo_position=False)
                return



class Selector(Entity):
    def input(self, key):
        if key == 'left mouse down':
            if mouse.hovered_entity:
                return

            clicked_entity = self.get_hovered_entity()

            if (
                clicked_entity in level_editor.entities
                and clicked_entity not in level_editor.selection
                and not held_keys['alt']
            ):
                if held_keys['shift']:
                    level_editor.selection.append(clicked_entity) # append
                else:
                    level_editor.selection = [clicked_entity, ]   # overwrite

            if held_keys['alt'] and clicked_entity in level_editor.selection:
                level_editor.selection.remove(clicked_entity) # remove

            if not clicked_entity and not held_keys['shift'] and not held_keys['alt']: # clear
                level_editor.selection.clear()

            level_editor.render_selection()

        if held_keys['control'] and key == 'a':
            level_editor.selection = list(level_editor.entities)
            level_editor.render_selection()

        elif key == 'h':
            level_editor.point_renderer.enabled = not level_editor.point_renderer.enabled


    def get_hovered_entity(self):
        entities_in_range = [(distance(e.screen_position, mouse.position), e) for e in level_editor.entities if e.selectable and not e.collider]
        entities_in_range = [e for e in entities_in_range if e[0] < .03]
        entities_in_range.sort()

        clicked_entity = None
        if entities_in_range:
            return entities_in_range[0][1]

        # try getting entities with box collider
        [setattr(e, 'collision', True) for e in level_editor.entities if not hasattr(e, 'is_gizmo')]
        mouse.update()

        if mouse.hovered_entity in level_editor.entities:
            [setattr(e, 'collision', False) for e in level_editor.entities if not hasattr(e, 'is_gizmo')]
            return mouse.hovered_entity

        [setattr(e, 'collision', False) for e in level_editor.entities if not hasattr(e, 'is_gizmo')]








class SelectionBox(Entity):
    def input(self, key):
        if key == 'left mouse down':
            if (
                mouse.hovered_entity
                and mouse.hovered_entity not in level_editor.selection
            ):
                # print('-------', 'clicked on gizmo, dont box select')
                return
            self.position = mouse.position
            self.scale = .001
            self.visible = True
            self.mode = 'new'
            if held_keys['shift']:
                self.mode = 'add'
            if held_keys['alt']:
                self.mode = 'subtract'

        if key == 'left mouse up' and self.visible:
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
                level_editor.selection.clear()

            for e in level_editor.entities:
                if not e.selectable:
                    continue

                pos = e.screen_position
                if pos.x > self.x and pos.x < self.x + abs(self.scale_x) and pos.y > self.y and pos.y < self.y + abs(self.scale_y):
                    if (
                        self.mode in ('add', 'new')
                        and e not in level_editor.selection
                    ):
                        level_editor.selection.append(e)
                    elif self.mode == 'subtract' and e in level_editor.selection:
                        level_editor.selection.remove(e)

            level_editor.render_selection()
            self.mode = 'new'

    def update(self):
        if mouse.left:
            if mouse.x == mouse.start_x and mouse.y == mouse.start_y:
                return

            self.scale_x = mouse.x - self.x
            self.scale_y = mouse.y - self.y


class Spawner(Entity):
    def __init__(self):
        super().__init__(parent=level_editor)
        self.target = None
        self.button = Button(parent=level_editor.ui, scale=.1, origin=(.5,-.5), position=window.bottom_right, text='+', on_click=self.spawn_entity)

    def input(self, key):
        if key == 'n':
            mouse.traverse_target = level_editor.grid
            self.spawn_entity()

        elif key == 'n up' and self.target:
            self.drop_entity()
            mouse.traverse_target = scene

        elif self.target and key == 'left mouse up':
            self.drop_entity()

    def spawn_entity(self):
        if not level_editor.current_scene:
            print_on_screen('<red>select a scene first', position=(0,0), origin=(0,0))
            return

        level_editor.grid.enabled = True
        self.target = Entity(model='cube', shader=lit_with_shadows_shader, position=mouse.world_point, original_parent=level_editor, selectable=True, collider='box', collision=False)
        level_editor.current_scene.entities.append(self.target)

    def drop_entity(self):
        level_editor.current_scene.undo.record_undo(('delete entities', [level_editor.current_scene.entities.index(self.target), ], [repr(self.target), ]))
        level_editor.selection = [self.target, ]
        level_editor.render_selection()
        self.target = None
        level_editor.grid.enabled = False


    def update(self):
        if mouse.world_point and self.target and (held_keys['n'] or mouse.left):
            self.target.position = mouse.world_point


class Deleter(Entity):
    def input(self, key):
        if level_editor.selection and key == 'delete':
            self.delete_selected()

    def delete_selected(self):
            level_editor.current_scene.undo.record_undo((
                'restore entities',
                [level_editor.entities.index(e) for e in level_editor.selection],
                [repr(e) for e in level_editor.selection],
                ))

            [level_editor.entities.remove(e) for e in level_editor.selection]
            [setattr(e, 'parent', level_editor) for e in level_editor.cubes]
            [destroy(e, delay=1/60) for e in level_editor.selection]
            level_editor.selection = []
            level_editor.render_selection()

# class OriginSetter(Entity):
#     def input(self, key):
#         if key == 'o':
#             if not level_editor.selection:
#                 return
#             if not len(set([e.origin for e in level_editor.selection])) == 1: # if seleciton has different origins, return
#                 return
#
#             if not hasattr(self, 'menu'):
#                 self.menu = Entity(parent=camera.ui, enabled=False)
#                 for i, e in enumerate(('x','y','z')):
#                     ButtonGroup(('-.5', '0', '.5'), parent=self.menu, y=-.05*i)
#
#             if not self.menu.enabled:
#                 self.menu.enabled = True
#
#                 for i, button_group in enumerate(self.menu.children):
#                     if str(level_editor.selection[0].origin[i]) in button_group.options:
#                         button_group.value = str(level_editor.selection[0].origin[i])
#
#             else:
#                 self.menu.enabled = False


class PointOfViewSelector(Entity):
    def __init__(self, **kwargs):

        super().__init__(parent=level_editor.ui, model='cube', collider='box', texture='white_cube', scale=.05, position=window.top_right-Vec2(.1,.1))
        self.front_text = Text(parent=self, text='front', z=-.5, scale=10, origin=(0,0), color=color.azure)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def on_click(self):
        if mouse.normal == Vec3(0,0,-1):   level_editor.editor_camera.animate_rotation((0,0,0)) # front
        elif mouse.normal == Vec3(0,0,1):  level_editor.editor_camera.animate_rotation((0,180,0)) # back
        elif mouse.normal == Vec3(1,0,0):  level_editor.editor_camera.animate_rotation((0,90,0)) # right
        elif mouse.normal == Vec3(-1,0,0): level_editor.editor_camera.animate_rotation((0,-90,0)) # right
        elif mouse.normal == Vec3(0,1,0):  level_editor.editor_camera.animate_rotation((90,0,0)) # top
        elif mouse.normal == Vec3(0,-1,0): level_editor.editor_camera.animate_rotation((-90,0,0)) # top


    def update(self):
        self.rotation = -level_editor.editor_camera.rotation

    def input(self, key):
        if key == '1':   level_editor.editor_camera.animate_rotation((0,0,0)) # front
        elif key == '3': level_editor.editor_camera.animate_rotation((0,90,0)) # right
        elif key == '7': level_editor.editor_camera.animate_rotation((90,0,0)) # top
        elif key == '5': camera.orthographic = not camera.orthographic


# class PaintBucket(Entity):
#     def input(self, key):
#         if held_keys['alt'] and key == 'c' and mouse.hovered_entity:
#             self.color = mouse.hovered_entity.color






class LevelMenu(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=level_editor)
        self.menu = Entity(parent=level_editor.ui, model=Quad(radius=.05), color=color.black, scale=.2, origin=(.5,0), x=camera.aspect_ratio*.495, collider='box')
        self.menu.grid = Entity(parent=self.menu, model=Grid(8,8), z=-1, origin=self.menu.origin, color=color.dark_gray)
        self.content_renderer = Entity(parent=self.menu, scale=1/8, position=(-1,-.5,-1), model=Mesh(), color='#222222') # scales the content so I can set the position as (x,y) instead of (-1+(x/8),-.5+(y/8))
        self.cursor = Entity(parent=self.content_renderer, model='quad', color=color.lime, origin=(-.5,-.5), z=-2, alpha=.5)
        self.current_scene_idicator = Entity(parent=self.content_renderer, model='circle', color=color.azure, origin=(-.5,-.5), z=-1, enabled=False)
        # self.tabs = [Button(parent=self.menu, scale=(1/4,1/8), position=(-1+(i/4),.5), origin=(-.5,-.5), color=color.hsv(90*i,.5,.3)) for i in range(4)]


        self.current_scene_label = Text(parent=self.menu, x=-1, y=-.5, text='current scene:', z=-10, scale=4)

        self.load_scenes()
        # self.goto_scene(0, 0)
        self.draw()


    def load_scenes(self):
        for scene_file in level_editor.scene_folder.glob('*.py'):
            if '__' in scene_file.name:
                continue

            print('found scene:', scene_file)
            name = scene_file.stem
            if '[' in name and ']' in name:
                x, y = (int(e) for e in name.split('[')[1].split(']')[0].split(','))
                print('scene is at coordinate:', x, y)
                level_editor.scenes[x][y].path = scene_file


    def draw(self):
        if not hasattr(self, 'quad_vertices'):
            self.quad_vertices = load_model('quad', application.internal_models_compressed_folder, use_deepcopy=True).vertices
            self.quad_vertices = [Vec3(*e)*.75 for e in self.quad_vertices]

        self.content_renderer.model.clear()
        for x in range(8):
            for y in range(8):
                if level_editor.scenes[x][y].path:
                    self.content_renderer.model.vertices += [Vec3(*v)+Vec3(x+.5,y+.5,0) for v in self.quad_vertices]

        self.content_renderer.model.generate()


    def update(self):
        self.cursor.enabled = self.menu.hovered
        if self.menu.hovered:
            grid_pos = [floor((mouse.point.x+1) * 8), floor((mouse.point.y+.5) * 8)]
            self.cursor.position = grid_pos


    def input(self, key):
        if held_keys['shift'] and key == 'm':
            self.menu.enabled = not self.menu.enabled

        # if key == 'left mouse down' and self.menu.hovered:
        #     self.click_start_pos = [int((mouse.point.x+1) * 8), int((mouse.point.y+.5) * 8)]

        if key == 'left mouse down' and self.menu.hovered:
            x, y = [int((mouse.point.x+1) * 8), int((mouse.point.y+.5) * 8)]
            # start_x, start_y = self.click_start_pos
            #
            # if x != start_x or y != start_y: # move scene
            #     print(f'move scene at {start_x},{start_y} to {x},{y}')
            #     scene_a = level_editor.scenes[start_x][start_y]
            #     scene_a.coordinates = (x,y)
            #     scene_a.name = scene_a.name.split('[')[0] + f'[{x},{y}]'
            #     if scene_a.path:
            #         scene_a.path = scene_a.path.parent / (scene_a.name + '.py')
            #
            #     scene_b = level_editor.scenes[x][y]
            #     scene_b.coordinates = (start_x, start_y)
            #     scene_b.name = scene_a.name.split('[')[0] + f'[{start_x},{start_y}]'
            #     if scene_b.path:
            #         scene_b.path = scene_b.path.parent / (scene_b.name + '.py')
            #
            #     # swap scenes
            #     level_editor.scenes[self.click_start_pos[0]][self.click_start_pos[1]], level_editor.scenes[x][y] = level_editor.scenes[x][y], level_editor.scenes[self.click_start_pos[0]][self.click_start_pos[1]]
            #
            #     self.draw()
            #     return
            # print(x, y)
            if not held_keys['shift'] and not held_keys['alt']:
                self.goto_scene(x, y)

            elif held_keys['shift'] and not held_keys['alt']: # append
                level_editor.scenes[x][y].load()

            elif not held_keys['shift']: # remove
                level_editor.scenes[x][y].unload()


        # hotkeys for loading neighbour levels
        if held_keys['shift'] and held_keys['alt'] and key in 'wasd':
            if not level_editor.current_scene:
                return

            coords = copy(level_editor.current_scene.coordinates)

            if key == 'd': coords[0] += 1
            if key == 'a': coords[0] -= 1
            if key == 'w': coords[1] += 1
            if key == 's': coords[1] -= 1

            # print(level_editor.current_scene.coordinates, '-->', coords)
            coords[0] = clamp(coords[0], 0, 8)
            coords[1] = clamp(coords[1], 0, 8)
            self.goto_scene(coords[0], coords[1])


        elif key == 'right mouse down' and self.hovered:
            x, y = [int((mouse.point.x+1) * 8), int((mouse.point.y+.5) * 8)]
            self.right_click_menu.enabled = True
            self.right_click_menu.position = (x,y)



    def goto_scene(self, x, y):
        self.current_scene_idicator.enabled = True
        self.current_scene_idicator.position = (x,y)
        [[level_editor.scenes[_x][_y].unload() for _x in range(8)] for _y in range(8)]
        level_editor.current_scene = level_editor.scenes[x][y]
        level_editor.current_scene.load()
        self.current_scene_label.text = level_editor.current_scene.name
        self.draw()
        level_editor.render_selection()

        try:
            sun_handler.sun.shadows = True
        except:
            print('no sun')

# class Inspector(Entity):
#     def __init__(self):
#         super().__init__(parent=level_editor.ui, enabled=True, position=(-.4*window.aspect_ratio,.5-(.05*.75)), model=Quad(aspect=3/2, radius=.05), origin=(-.5,.5), scale=(.25,.2), color=color.black66, collider='box')
#         self.name_field = InputField(default_value='entity')
#         self.name_field.scale *= .75
#         # self.background = Entity(parent=self, model=Quad(aspect=2), radius=.1, color=color.black66, scale=.25)
#         self.position_field = Button(scale=(.1, .05), world_parent=self, )
#
#         # self.scale *= .75
#
#     def render(self):
#         pass



class ModelMenu(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=level_editor)
        self.button_list = None     # gets created on self.open()

    def open(self):
        # self.model_names = [e.stem for e in application.internal_models_compressed_folder.glob('**/*.ursinamesh')]
        self.model_names = ['cube', 'sphere', 'plane']
        for file_type in ('.bam', '.obj', '.ursinamesh'):
            self.model_names += [
                e.stem
                for e in application.asset_folder.glob(f'**/*{file_type}')
                if 'animation' not in e.stem
            ]


        # print('mmmmmmm', self.model_names)
        model_dict = {name : Func(self.set_models_for_selection, name) for name in self.model_names}
        if not self.button_list:
            self.button_list = ButtonList(model_dict, font='VeraMono.ttf')
            self.bg = Entity(parent=self.button_list, model='quad', collider='box', color=color.black33, on_click=self.button_list.disable, z=.1, scale=100)
        else:
            self.button_list.enabled = True

        self.button_list.position = mouse.position


    def input(self, key):

        if key == 'm' and level_editor.selection:
            self.open()

    def set_models_for_selection(self, name):
        for e in level_editor.selection:
            e.model = name

        self.button_list.enabled = False

class TextureMenu(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=level_editor)
        self.button_list = None     # gets created on self.open()


    def open(self):
        self.asset_names = []
        self.asset_names = [e.stem for e in application.internal_textures_folder.glob('**/*.png')]

        for file_type in ('.png', '.jpg', '.jpeg'):
            self.asset_names += [e.stem for e in application.asset_folder.glob(f'**/*{file_type}')]

        if not self.asset_names:
            print('no texture assets found')
            return

        texture_dict = {name : Func(self.set_texture_for_selection, name) for name in self.asset_names}
        if not self.button_list:
            self.button_list = ButtonList(texture_dict, font='VeraMono.ttf')
            self.bg = Entity(parent=self.button_list, model='quad', collider='box', color=color.black33, on_click=self.button_list.disable, z=.1, scale=100)
        else:
            self.button_list.enabled = True

    def input(self, key):
        if key == 'v' and level_editor.selection:
            self.open()

    def set_texture_for_selection(self, name):
        for e in level_editor.selection:
            e.texture = name

        self.button_list.enabled = False

class ColorMenu(Entity):
    def __init__(self):
        super().__init__(parent=level_menu)
        self.sub_menu = Entity(parent=level_editor.ui, enabled=False)

        self.h_slider = Slider(name='h', min=0, max=360, step=1, text='h', dynamic=True, world_parent=self.sub_menu, on_value_changed=self.on_slider_changed)
        self.h_slider.bg.color = color.white
        self.h_slider.bg.texture = 'rainbow'
        self.h_slider.bg.texture.filtering = True

        self.s_slider = Slider(name='s', min=0, max=100, step=1, default=50, text='s', dynamic=True, world_parent=self.sub_menu, on_value_changed=self.on_slider_changed)
        self.s_slider.bg.color = color.white
        self.s_slider.bg.model.colors = [color.white for i in self.s_slider.bg.model.vertices]

        self.v_slider = Slider(name='v', min=0, max=100, default=50, step=1, text='v', dynamic=True, world_parent=self.sub_menu, on_value_changed=self.on_slider_changed)
        self.v_slider.bg.model.colors = [color.black for i in self.v_slider.bg.model.vertices]
        self.v_slider.bg.color = color.white

        self.a_slider = Slider(name='a', min=0, max=100, default=100, step=1, text='a', dynamic=True, world_parent=self.sub_menu, on_value_changed=self.on_slider_changed)
        self.a_slider.bg.model.colors = [color.white for i in self.a_slider.bg.model.vertices]
        self.a_slider.bg.color = color.white
        for i, v in enumerate(self.a_slider.bg.model.vertices):
            if v[0] < 0:
                self.a_slider.bg.model.colors[i] = color.clear
        self.a_slider.bg.model.generate()

        for i, e in enumerate((self.h_slider, self.s_slider, self.v_slider, self.a_slider)):
            e.y = -i * .03
            e.knob.color = color.white

        self.sub_menu.scale *= .6

        self.bg = Entity(parent=self.sub_menu, model='quad', collider='box', visible_self=False, scale=10, z=1, on_click=self.close)
        self.apply_color = True     # set to False when you want to move the sliders but not update the color of the entities.


    def on_slider_changed(self):
        value = color.hsv(self.h_slider.value, self.s_slider.value/100, self.v_slider.value/100, self.a_slider.value/100)

        if self.apply_color:
            for e in level_editor.selection:
                e.color = value

        for i, v in enumerate(self.s_slider.bg.model.vertices):
            if v[0] < 0:
                self.s_slider.bg.model.colors[i] = color.gray
            else:
                self.s_slider.bg.model.colors[i] = color.hsv(value.h, 1, value.v)

        self.s_slider.bg.model.generate()

        for i, v in enumerate(self.v_slider.bg.model.vertices):
            if v[0] > 0:
                self.v_slider.bg.model.colors[i] = color.hsv(value.h, value.s, 1)

        self.v_slider.bg.model.generate()

        self.a_slider.bg.color = value

    def input(self, key):
        if key == 'b' and not held_keys['control'] and not held_keys['shift'] and not held_keys['alt']:
            self.open()

    def open(self):
        if self.sub_menu.enabled:
            return

        for e in level_editor.selection:
            e.original_color = e.color

        self.sub_menu.enabled = True
        self.apply_color = False
        self.h_slider.value = level_editor.selection[0].color.h * 360
        self.s_slider.value = level_editor.selection[0].color.s * 100
        self.v_slider.value = level_editor.selection[0].color.v * 100
        self.a_slider.value = level_editor.selection[0].color.a * 100
        self.apply_color = True



    def close(self):
        self.sub_menu.enabled = False
        level_editor.current_scene.undo.record_undo([(level_editor.entities.index(e), 'color', e.original_color, e.color) for e in level_editor.selection])


class Help(Button):
    def __init__(self, **kwargs):
        super().__init__(parent=level_editor.ui, text='?', scale=.025, model='circle', origin=(-.5,.5), text_origin=(0,0), position=window.top_left)
        self.tooltip = Text(
            position=self.position + Vec3(.05,-.05,-1),
            # wordwrap=0,
            font='VeraMono.ttf',
            enabled=False,
            text=dedent('''
                Hotkeys:
                n:          add new cube
                w:          move tool
                g:          quick move
                x/y/z:      hold to quick move on axis
                c:          quick rotate
                e:          scale tool
                s:          quick scale
                s + x/y/z:  quick scale on axis
                f:          move editor camera to point
                shift+f:    reset editor camera position
                shift+p:    toggle perspective/orthographic
                shift+d:    duplicate
            ''').strip(),
            background=True
        )

class Duplicator(Entity):
    def input(self, key):
        if held_keys['shift'] and key == 'd' and level_editor.selection:
            clones = [duplicate(e, original_parent=level_editor.current_scene, color=e.color, shader=e.shader, origin=e.origin, parent=level_editor.current_scene, selectable=e.selectable) for e in level_editor.selection]
            [level_editor.entities.append(e) for e in clones]
            level_editor.selection = clones
            level_editor.current_scene.undo.record_undo(('delete entities', [level_editor.entities.index(en) for en in clones], [repr(e) for e in clones],))

            level_editor.render_selection()
            gizmo.drag()
            gizmo.subgizmos['xz'].start_dragging()



class PokeShape(Entity):
    def __init__(self, points=[Vec3(-.5,0,-.5), Vec3(.5,0,-.5), Vec3(.5,0,.5), Vec3(-.5,0,.5)], **kwargs):
        # if 'parent' in kwargs.keys():
        #     del kwargs['parent']


        super().__init__(original_parent=level_editor, model=Mesh(), selectable=True, name='poke_shape', **kwargs)
        level_editor.entities.append(self)

        self.point_gizmos = LoopingList([Entity(parent=self, original_parent=self, position=e, selectable=False, name='PokeShape_point', is_gizmo=True) for e in points])
        self.edit_mode = False

        self.add_collider = False

        self.make_wall = True
        self.wall_parent = None
        if self.make_wall:
            self.wall_parent = Entity(parent=self, model=Mesh(), color=color.dark_gray, add_to_scene_entities=False)

        self.wall_height = 1
        self.wall_thickness = .1

        self.generate()


    def generate(self):
        import tripy
        polygon = LoopingList(e.get_position(relative_to=self).xz for e in self.point_gizmos)
        triangles = tripy.earclip(polygon)
        self.model.vertices = []
        for tri in triangles:
            for v in tri:
                self.model.vertices.append(Vec3(v[0], 0, v[1]))

        self.model.uvs = [Vec2(v[0],v[2])*1 for v in self.model.vertices]
        self.model.normals = [Vec3(0,1,0) for i in range(len(self.model.vertices))]
        self.model.generate()
        self.texture = 'grass'


        if self.make_wall:
            wall_verts = []
            for i, vert in enumerate(polygon):
                vert = Vec3(vert[0], 0, vert[1])
                next_vert = Vec3(polygon[i+1][0], 0, polygon[i+1][1])

                wall_verts.extend((
                    vert,
                    vert + Vec3(0,-1,0),
                    next_vert,

                    next_vert,
                    vert + Vec3(0,-1,0),
                    next_vert + Vec3(0,-1,0),
                ))

            self.wall_parent.model.vertices = wall_verts
            self.wall_parent.model.generate()



        if self.add_collider:
            self.collider = self.model

    def __repr__(self):
        default_values = {
            # 'parent':'scene',
            'enabled':True, 'position':Vec3(0,0,0), 'rotation':Vec3(0,0,0), 'scale':Vec3(1,1,1), 'origin':Vec3(0,0,0),
            'texture':None, 'color':color.white, 'collider':None, 'points':[Vec3(-.5,0,-.5), Vec3(.5,0,-.5), Vec3(.5,0,.5), Vec3(-.5,0,.5)]}

        changes = []
        for key, value in default_values.items():
            if getattr(self, key) != default_values[key]:
                if key == 'texture':
                    changes.append(f"texture='{getattr(self, key).name.split('.')[0]}', ")
                    continue

                value = getattr(self, key)
                if isinstance(value, str):
                    value = f"'{repr(value)}'"

                changes.append(f"{key}={value}, ")

        return f'{__class__.__name__}(' +  ''.join(changes) + ')'


    @property
    def points(self):
        return [e.position for e in self.point_gizmos]

    @property
    def edit_mode(self):
        return self._edit_mode

    @edit_mode.setter
    def edit_mode(self, value):
        print('set edit mode', value)
        self._edit_mode = value
        if value:
            [setattr(e, 'selectable', False) for e in level_editor.entities if e != self]
            for e in self.point_gizmos:
                if e not in level_editor.entities:
                    level_editor.entities.append(e)

            [setattr(e, 'selectable', True) for e in self.point_gizmos]
            gizmo.subgizmos['y'].enabled = False
            gizmo.fake_gizmo.subgizmos['y'].enabled = False

        else:
            print(self.point_gizmos[0] in level_editor.entities)
            [level_editor.entities.remove(e) for e in self.point_gizmos]
            [setattr(e, 'selectable', True) for e in level_editor.entities]
            if True in [e in level_editor.selection for e in self.point_gizmos]: # if point is selected when exiting edit mode, select the poke shape
                level_editor.selection = [self, ]

            gizmo.subgizmos['y'].enabled = True
            gizmo.fake_gizmo.subgizmos['y'].enabled = True

        level_editor.render_selection()


    # def update(self):
    #     if self.edit_mode:
    #         if mouse.left or held_keys['g']:
    #             level_editor.render_selection()
    #             self.generate()


    def input(self, key):
        if key == 'tab':
            if self in level_editor.selection or True in [e in level_editor.selection for e in self.point_gizmos]:
                self.edit_mode = not self.edit_mode

        elif key == 'left mouse down' and self.edit_mode and selector.get_hovered_entity():
            level_editor.selection.clear()
            selection_box.enabled = False
            quick_grabber.input('g')

        elif key == 'left mouse up' and self.edit_mode:
            quick_grabber.input('g up')
            selection_box.enabled = True

        elif key == '+' and len(level_editor.selection) == 1 and level_editor.selection[0] in self.point_gizmos:
            print('add point')
            i = self.point_gizmos.index(level_editor.selection[0])

            new_point = Entity(parent=self, original_parent=self, position=lerp(self.point_gizmos[i].position, self.point_gizmos[i+1].position, .5), selectable=True, is_gizmo=True)
            level_editor.entities.append(new_point)
            self.point_gizmos.insert(i+1, new_point)
            level_editor.render_selection()
            # self.generate()


        elif key == 'space':
            self.generate()

        elif key == 'double click' and level_editor.selection == [self, ] and selector.get_hovered_entity() == self:
            self.edit_mode = not self.edit_mode

        elif self.edit_mode and key.endswith(' up'):
            invoke(self.generate, delay=3/60)


class SunHandler(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sun = DirectionalLight(parent=level_editor, shadow_map_resolution=(2048,2048))
        self.sun.look_at(Vec3(-2,-1,-1))

        # def input(self, key):
        #     if key == 'l':
        #         for e in level_editor.entities:
        #             e.shader = unlit_shader
        #             e.unlit = not e.unlit
from ursina.prefabs.radial_menu import RadialMenu
class RightClickMenu(Entity):
    def __init__(self):
        super().__init__()
        self.radial_menu = RadialMenu(
            parent=level_editor.ui,
            buttons = (
                Button(highlight_color=color.azure, text='Model', on_click=model_menu.open),
                Button(highlight_color=color.azure, text='Tex', on_click=texture_menu.open),
                Button(highlight_color=color.azure, text='Col', on_click=color_menu.open),
                Button(highlight_color=color.azure, text='Sh'),
                Button(highlight_color=color.black, text='del', scale=.5, color=color.red, on_click=deleter.delete_selected),
                Button(highlight_color=color.azure, text='collider'),
            ),
            enabled=False,
            scale=.05
        )

    def input(self, key):
        if key == 'right mouse down':
            self.start_click_pos = mouse.position

        if (
            key == 'right mouse up'
            and level_editor.selection
            and sum(abs(e) for e in mouse.position - self.start_click_pos) < 0.005
        ):
            self.radial_menu.enabled = True





if __name__ == '__main__':
    app = Ursina(size=(1280,720))
    # app = Ursina(vsync=False)


level_editor = LevelEditor()


# AmbientLight(color=color._16)
sun_handler = SunHandler(parent=level_editor)

for x in range(8):
    for y in range(8):
        level_editor.scenes[x][y].undo = Undo()

gizmo = Gizmo()
level_editor.gizmo = gizmo
rotation_gizmo = RotationGizmo()
scale_gizmo = ScaleGizmo()
box_gizmo = BoxGizmo()
gizmo_toggler = GizmoToggler(parent=level_editor)

quick_grabber = QuickGrabber(parent=level_editor)   # requires gizmo, selector
QuickScaleOrRotate()    # requires scale_gizmo, gizmo_toggler, selector
selector = Selector(parent=level_editor)
selection_box = SelectionBox(parent=level_editor.ui, model=Quad(0, mode='line'), origin=(-.5,-.5,0), scale=(0,0,1), color=color.white33, mode='new')
spawner = Spawner()
deleter = Deleter(parent=level_editor)
level_menu = LevelMenu()
goto_scene = level_menu.goto_scene
duplicator = Duplicator()

model_menu = ModelMenu()
texture_menu = TextureMenu()
color_menu = ColorMenu()
right_click_menu = RightClickMenu()
# OriginSetter(parent=level_editor)
PointOfViewSelector()
Help()


debug_text = Text(y=-.45)

def update():
    if level_editor.selection:
        e = level_editor.selection[-1]
        r = round(camera.back.dot(e.right), 1)
        u = round(camera.back.dot(e.up), 1)
        f = round(camera.back.dot(e.forward), 1)
        dir = (r, u, f)
        axis_index = dir.index(max(dir, key=abs))
        # is_positive_direction = dir[axis_index] > 0

        # print(axis_index, is_positive_direction)
        # dir =
        # print('f:', camera.forward.dot(e.forward))
        # print('u:', camera.forward.dot(e.up))
        # print('r:', camera.forward.dot(e.right))
        # print('a')
        # debug_text.text = f'{round(Vec3(*level_editor.selection[-1].forward.normalized()), 0) + round(Vec3(*look_at_angle_helper.forward), 0)}'

# inspector = Inspector()

# inspector = WindowPanel(
#     title='entity',
#     content=(
#         # InputField(name='name_field'),
#         (Button(text='0'), Button()),
#         Text('Name:'),
#         # Text('Age:'),
#         # InputField(name='age_field'),
#         # Text('Phone Number:'),
#         # InputField(name='phone_number_field'),
#         # Space(height=1),
#         # Text('Send:'),
#         Slider(),
#         Slider(),
#         # ButtonGroup(('test', 'eslk', 'skffk'))
#         ),
#         # popup=True,
#         # enabled=False,
#         parent=level_editor.ui,
#     )
# inspector = Entity(parent=level_editor.ui, position=window.top_left+Vec2(.1,-.05))
# for y in range(3):
#     for x in range(3):
#         b = Button(scale=(.12,.033), text='013', parent=inspector, origin=(-.5,.5), position=(x*.121,-y*.035), radius=.5, text_origin=(-.5,0))
#         b.text_entity.x += .1
#
#
# inspector.background = Entity(parent=inspector, model=Quad(radius=.05), origin_y=.5, scale=(.12*3)+.01, position=((.12*3/2),.01), color=color.black66)
# inspector.scale = .5


#
# level_editor_toggler = Entity()
# def level_editor_toggler_input(key):
#     if key == 'escape':
#         level_editor.enabled = not level_editor.enabled
#
# level_editor_toggler.input = level_editor_toggler_input



# class Debug(Entity):
#     def input(self, key):
#         if key == 'space':
#             print(level_editor.selection)
#             # for e in level_editor.entities:
#             #     print(e.__class__.__name__)
# Debug()
    # t = Text(position=window.top_left + Vec2(.01,-.06))
    # def update():
    #     t.text = 'selection:\n' + '\n'.join([str(e) for e in level_editor.selection])
if __name__ == '__main__':
    goto_scene(2,0)
    # from poke_shape import PokeShape
    # poke_shape = PokeShape(scale=4, points=[Vec3(-.5,0,-.5), Vec3(.5,0,-.5), Vec3(.5,0,-.25), Vec3(.75,0,-.25), Vec3(.75,0,.25), Vec3(.5,0,.25), Vec3(.5,0,.5), Vec3(-.5,0,.5)])
    # poke_shape = PokeShape(scale=4, points=[Vec3(-.5,0,-.5), Vec3(.5,0,-.5), Vec3(.5,0,-.25), Vec3(.75,0,-.25), Vec3(.75,0,.25), Vec3(.5,0,.25), Vec3(.5,0,.5), Vec3(.5,0,.55), Vec3(-.5,0,.5)])
    # level_editor.entities.append(poke_shape)
    app.run()
