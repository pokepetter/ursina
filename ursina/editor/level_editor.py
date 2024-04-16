from ursina import *
from ursina.shaders import unlit_shader, lit_with_shadows_shader, matcap_shader, triplanar_shader, normals_shader
from time import perf_counter
import csv
import builtins
import pyperclip
import inspect


class LevelEditor(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        builtins.LEVEL_EDITOR = self
        self.scene_folder = application.asset_folder / 'scenes'
        self.scenes = [[LevelEditorScene(x, y, f'untitled_scene[{x},{y}]') for y in range(8)] for x in range(8)]
        self.current_scene = None

        self.grid = Entity(parent=self, model=Grid(16,16), rotation_x=90, scale=64, collider='box', color=color.white33, enabled=False)
        self.origin_mode = 'center'
        self.editor_camera = EditorCamera(parent=self, rotation_x=20, eternal=False, rotation_smoothing=0)
        original_editor_camera_rotation_speed = self.editor_camera.rotation_speed
        def _update():
            self.editor_camera.rotation_speed = original_editor_camera_rotation_speed * int(not mouse.left)   # don't rotate when holding left mouse button
        Entity(parent=self.editor_camera, update=_update)


        self.ui = Entity(parent=camera.ui, name='LEVEL_EDITOR.ui')
        self.point_renderer = Entity(parent=self, model=Mesh([], mode='point', thickness=.1, render_points_in_3d=True), texture='circle_outlined', always_on_top=True, unlit=True, render_queue=1)
        self.cubes = [Entity(wireframe=True, color=color.azure, parent=self, enabled=True) for i in range(128)] # max selection

        self.origin_mode_menu = ButtonGroup(['last', 'center', 'individual'], min_selection=1, position=window.top, parent=self.ui)
        self.origin_mode_menu.scale *= .5
        self.origin_mode_menu.on_value_changed = self.render_selection
        self.local_global_menu = ButtonGroup(['local', 'global'], default='global', min_selection=1, position=window.top - Vec2(.2,0), parent=self.ui)
        self.local_global_menu.scale *= .5
        self.local_global_menu.on_value_changed = self.render_selection
        self.target_fov = 90

        self.sun_handler = SunHandler()
        self.sky = Sky(parent=scene)
        self.gizmo = Gizmo()
        self.rotation_gizmo = RotationGizmo()
        self.scale_gizmo = ScaleGizmo()
        self.box_gizmo = BoxGizmo()
        self.gizmo_toggler = GizmoToggler()

        self.quick_grabber = QuickGrabber()   # requires gizmo, selector
        self.quick_scaler = QuickScaler()    # requires scale_gizmo, gizmo_toggler, selector
        self.quick_rotator = QuickRotator()
        self.rotate_to_view = RotateRelativeToView(target_entity=None)
        self.selector = Selector()
        self.selection_box = SelectionBox(model=Quad(0, mode='line'), origin=(-.5,-.5,0), scale=(0,0,1), color=color.white33, mode='new')

        self.prefab_folder = application.asset_folder / 'prefabs'
        from ursina.editor.prefabs.poke_shape import PokeShape
        # from ursina.editor.prefabs.sliced_cube import SlicedCube
        # print('-----------------', PokeShape)
        self.built_in_prefabs = [ClassSpawner, WhiteCube, TriplanarCube, Pyramid, PokeShape]
        self.prefabs = []
        self.spawner = Spawner()
        self.deleter = Deleter()
        self.grouper = Grouper()
        self.level_menu = LevelMenu()
        self.goto_scene = self.level_menu.goto_scene
        self.duplicator = Duplicator()
        self.copier = Copier()

        self.model_menu = ModelMenu()
        self.texture_menu = TextureMenu()
        self.color_menu = ColorMenu()
        self.shader_menu = ShaderMenu()
        self.collider_menu = ColliderMenu()
        self.class_menu = ClassMenu()
        self.menu_handler = MenuHandler()
        self.right_click_menu = RightClickMenu()
        self.hierarchy_list = HierarchyList()
        self.inspector = Inspector()
        self.point_of_view_selector = PointOfViewSelector()
        self.help = Help()

        self._edit_mode = True

    def add_entity(self, entity):
        for key, value in dict(original_parent=LEVEL_EDITOR, selectable=True, collision=False, collider_type='None').items():
            # print('set', key, value)
            if not hasattr(entity, key):
                setattr(entity, key, value)

        LEVEL_EDITOR.current_scene.entities.append(entity)


    @property
    def entities(self):
        if not self.current_scene:
            return []
        return self.current_scene.entities

    @entities.setter
    def entities(self, value):
        if not self.current_scene:
            return
        self.current_scene.entities = value

    @property
    def selection(self):
        if not self.current_scene:
            return []
        return self.current_scene.selection

    @selection.setter
    def selection(self, value):
        if not self.current_scene:
            return
        self.current_scene.selection = value

    def on_enable(self):
        self._camera_original_fov = camera.fov
        camera.fov = self.target_fov

    def on_disable(self):
        camera.fov = self._camera_original_fov

    def update(self):
        for key in 'gsxyz':
            if held_keys[key]:
                self.render_selection()
                return

        if mouse.left:
            self.render_selection()


    def input(self, key):
        if held_keys['control'] and not held_keys['shift'] and not held_keys['alt'] and key == 's':
            if not self.current_scene:
                print("no current_scene, can't save")
                return

            self.current_scene.save()

        if held_keys['control']:
            if key == 'z' and self.current_scene:
                self.current_scene.undo.undo()
            elif key == 'y' and self.current_scene:
                self.current_scene.undo.redo()

        if self.selection and key == 'f':
            self.editor_camera.animate_position(self.gizmo.world_position, duration=.1, curve=curve.linear)

        if held_keys['control'] and key == 'e':
            self.edit_mode = not self.edit_mode


    @property
    def edit_mode(self):
        return self._edit_mode

    @edit_mode.setter
    def edit_mode(self, value):
        if not value and self._edit_mode:   # enter play mode
            for e in self.children:
                e.ignore = True
                e.visible = False

            self.editor_camera.original_target_z = self.editor_camera.target_z
            self.editor_camera.enabled = False
            self.ui.enabled = False
            for e in self.current_scene.entities:
                # switch editor colliders out for what they should have during play
                if hasattr(e, 'edit_mode') and e.edit_mode:
                    e.edit_mode = False

                e.editor_collider = e.collider
                if e.collider:
                    e.editor_collider = e.collider.name

                if hasattr(e, 'collider_type') and e.collider_type != 'None':
                    e.collider = e.collider_type
                else:
                    e.collider = None


                if hasattr(e, 'start') and callable(e.start):
                    e.start()

        elif value and not self._edit_mode: # back to editor mode
            self.ui.enabled = True
            for e in self.current_scene.entities:
                if hasattr(e, 'stop') and callable(e.stop):
                    e.stop()
                e.collider = e.editor_collider

            for e in self.children:
                e.ignore = False
                e.visible = True

            self.editor_camera.enabled = True
            self.editor_camera.target_z = self.editor_camera.original_target_z
            camera.z = self.editor_camera.target_z

        self._edit_mode = value
        # print('set edit mode to', value)


    def render_selection(self, update_gizmo_position=True):
        for i, e in enumerate(self.entities):
            if e == None:
                print(f'error in entities {i}, is {e}')
                self.entities.remove(e)

        # self.point_renderer.model.vertices = [e.world_position for e in self.entities if e.selectable and not e.model ]
        self.point_renderer.model.vertices = []
        self.point_renderer.model.colors = []

        for e in self.entities:
            if not e or e.model and e.model.name == 'cube':
                continue

            self.point_renderer.model.vertices.append(e.world_position)

            if not e in self.selection:
                gizmo_color = color.orange
                if hasattr(e.__class__, 'gizmo_color'):
                    gizmo_color = e.__class__.gizmo_color

                self.point_renderer.model.colors.append(gizmo_color)
            else:
                gizmo_color = color.azure
                if hasattr(e.__class__, 'gizmo_color_selected'):
                    gizmo_color = e.__class__.gizmo_color_selected
                self.point_renderer.model.colors.append(gizmo_color)


        # self.point_renderer.model.colors = [color.azure if e in self.selection else lerp(color.orange, color.hsv(0,0,1,0), distance(e.world_position, camera.world_position)/100) for e in self.entities if e.selectable and not e.collider]
        self.point_renderer.model.triangles = []
        # print('--------------', len(self.point_renderer.model.vertices), len(self.point_renderer.model.colors), self.point_renderer.model.recipe)
        self.point_renderer.model.generate()

        # self.gizmo.enabled = bool(self.selection and self.selection[-1])
        self.selection = [e for e in self.selection if e]

        if update_gizmo_position and self.selection:
            if self.origin_mode_menu.value in ('last', 'individual'):
                self.gizmo.world_position = self.selection[-1].world_position
            elif self.origin_mode_menu.value == 'center':
                self.gizmo.world_position = sum([e.world_position for e in self.selection]) / len(self.selection)

            if self.local_global_menu.value == 'local' and self.origin_mode_menu.value == 'last':
                self.gizmo.world_rotation = self.selection[-1].world_rotation
            else:
                self.gizmo.world_rotation = Vec3(0,0,0)

        [e.disable() for e in self.cubes]
        # [setattr(e, 'parent', self) for e in self.cubes]
        for i, e in enumerate([e for e in self.selection if e.collider]):
            if i < len(self.cubes):
                self.cubes[i].world_transform = e.world_transform
                self.cubes[i].origin = e.origin
                self.cubes[i].model = copy(e.model)
                self.cubes[i].enabled = True

        # print('---------- rendered selection')

        LEVEL_EDITOR.hierarchy_list.render_selection()


    def on_enable(self):
        if hasattr(self, 'ui'):
            self.ui.enabled = True

    def on_disable(self):
        self.ui.enabled = False

class ErrorEntity(Entity):
    def __init__(self, model='wireframe_cube', color=color.red, **kwargs):
        super().__init__(model=model, color=color, **kwargs)

class LevelEditorScene:
    def __init__(self, x, y, name, **kwargs):
        super().__init__()
        self.coordinates = [x,y]
        self.name = name
        self.path = None    # must be assigned to be able to load
        self.entities = []
        self.selection = []
        self.scene_parent = None
        self.undo = Undo()
        # self.undo_handler     # gets assigned later

    def save(self):
        if not self.path and not self.entities:
            print('cant save scene with not path and no entities')
            return

        LEVEL_EDITOR.scene_folder.mkdir(parents=True, exist_ok=True)
        list_of_dicts = []

        fields = ['class', ]
        for e in LEVEL_EDITOR.current_scene.entities:
            if hasattr(e, 'is_gizmo'):
                continue

            changes = e.get_changes(e.__class__)
            for key, value in changes.items():
                if value == None:
                    changes[key] = False
            # if 'subdivisions' in changes:
            changes['class'] = e.__class__.__name__
            if hasattr(e, 'collider_type'):
                changes['collider_type'] = f"'{e.collider_type}'"
            print('changes:', changes)
            list_of_dicts.append(changes)
            for key in changes.keys():
                if key not in fields:
                    fields.append(key)


        name = LEVEL_EDITOR.current_scene.name
        self.path =  LEVEL_EDITOR.scene_folder / f'{name}.csv'

        with self.path.open('w', encoding='UTF8') as file:
            writer = csv.DictWriter(file, fieldnames=fields, delimiter=';')
            writer.writeheader()
            writer.writerows(list_of_dicts)

        print('saved:', self.path)


    def load(self):
        if not self.path:
            print('cant load scene, no path')
            return
        if self.scene_parent:
            print('error, scene already loaded')
            return

        # get all imported classes
        imported_classes = dict()
        for module_name, module in list(sys.modules.items()):
            if hasattr(module, '__file__') and module.__file__ and not module.__file__.startswith(sys.prefix):  # filter out built-in modules and modules from the standard library
                for _, obj in inspect.getmembers(module):
                    if inspect.isclass(obj):
                        imported_classes[obj.__name__] = obj

        t = perf_counter()
        with self.path.open('r') as f:
            self.scene_parent = Entity()
            reader = csv.DictReader(f, delimiter=';')
            fields = reader.fieldnames[1:]

            for line in reader:
                kwargs = {key : value for key, value in line.items() if value and not key == 'class'}
                if not 'parent' in kwargs:
                    kwargs['parent'] = self.scene_parent

                for key, value in kwargs.items():
                    if key == 'parent':
                        continue

                    try:
                        value = eval(value)
                        kwargs[key] = value
                    except:
                        pass

                if not line["class"] in imported_classes:
                    target_class = ErrorEntity
                else:
                    target_class = imported_classes[line["class"]]


                instance = target_class(**kwargs)
                self.entities.append(instance)


                for e in self.entities:
                    if not e.shader:
                        e.shader = lit_with_shadows_shader
                    e.selectable = True

                    if not hasattr(e, 'collider_type'):
                        e.collider_type = None

                    e.original_parent = e.parent
                    if e.model and e.model.name == 'cube':
                        e.collider = 'box'
                        e.collision = False


        if self.scene_parent:
            print(f'loaded scene: "{self.name}" in {perf_counter()-t}')
            return self.scene_parent


    def unload(self):
        [setattr(e, 'parent', LEVEL_EDITOR) for e in LEVEL_EDITOR.cubes]
        [destroy(e) for e in self.entities]
        # if not self.scene_parent:
        #     # print('cant unload scene, its already empty')
        #     return

        self.selection = []
        self.entities = []
        destroy(self.scene_parent)


class Undo(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=LEVEL_EDITOR, undo_data=[], undo_index=-1)

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
                LEVEL_EDITOR.entities.insert(id, clone)

        elif current_undo_data[0] == 'delete entities': # delete newly created entity
            target_entities = [LEVEL_EDITOR.entities[id] for id in current_undo_data[1]]
            [LEVEL_EDITOR.selection.remove(e) for e in target_entities if e in LEVEL_EDITOR.selection]
            [setattr(e, 'parent', LEVEL_EDITOR) for e in LEVEL_EDITOR.cubes]
            [LEVEL_EDITOR.entities.remove(e) for e in target_entities]
            [destroy(e) for e in target_entities]

        else:
            for data in current_undo_data:
                id, attr, original, new = data
                setattr(LEVEL_EDITOR.entities[id], attr, original)

        LEVEL_EDITOR.render_selection()     # make sure the gizmo position updates
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
                LEVEL_EDITOR.entities.insert(id, clone)

        elif current_undo_data[0] == 'restore entities': # restore entity
            pass
            target_entities = [LEVEL_EDITOR.entities[id] for id in current_undo_data[1]]
            [LEVEL_EDITOR.selection.remove(e) for e in target_entities if e in LEVEL_EDITOR.selection]
            [setattr(e, 'parent', LEVEL_EDITOR) for e in LEVEL_EDITOR.cubes]
            [LEVEL_EDITOR.entities.remove(e) for e in target_entities if e in LEVEL_EDITOR.entities]
            [destroy(e) for e in target_entities]


        else:
            for data in current_undo_data:
                id, attr, original, new = data
                setattr(LEVEL_EDITOR.entities[id], attr, new)

        LEVEL_EDITOR.render_selection()     # make sure the gizmo position updates
        self.undo_index += 1


axis_colors = {
    'x' : color.magenta,
    'y' : color.yellow,
    'z' : color.cyan
}

if not load_model('arrow', application.internal_models_compressed_folder):
    p = Entity(enabled=False)
    Entity(parent=p, model='cube', scale=(1,.05,.05))
    Entity(parent=p, model=Cone(4), x=.5, scale=.2, rotation=(0,90,0))
    arrow_model = p.combine()
    arrow_model.save('arrow.ursinamesh', folder=application.internal_models_compressed_folder, max_decimals=4)

if not load_model('scale_gizmo', application.internal_models_compressed_folder):
    p = Entity(enabled=False)
    Entity(parent=p, model='cube', scale=(.05,.05,1))
    Entity(parent=p, model='cube', z=.5, scale=.2)
    arrow_model = p.combine()
    arrow_model.save('scale_gizmo.ursinamesh', folder=application.internal_models_compressed_folder, max_decimals=4)


class GizmoArrow(Draggable):
    def __init__(self, model='arrow', collider='box', **kwargs):
        super().__init__(model=model, origin_x=-.55, always_on_top=True, render_queue=1, is_gizmo=True, shader=unlit_shader, **kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.record_undo = True     # this can be set to False when moving this though code for example, and you don't want it to record undo.
        self.original_rotation = self.rotation


    def drag(self):
        self.world_parent = LEVEL_EDITOR
        LEVEL_EDITOR.gizmo.world_parent = self
        for e in LEVEL_EDITOR.selection:
            if not hasattr(e.parent, 'is_gizmo') or e.parent.is_gizmo == False:
                e.original_parent = e.parent
            else:
                e.original_parent = scene

            if LEVEL_EDITOR.local_global_menu.value == 'global':
                e.world_parent = self
            else:
                e.world_parent = LEVEL_EDITOR.gizmo.fake_gizmo

            e.always_on_top = False
            e._original_world_transform = e.world_transform

    def drop(self):
        LEVEL_EDITOR.gizmo.world_parent = LEVEL_EDITOR

        for e in LEVEL_EDITOR.selection:
            e.world_parent = e.original_parent
            print('---------------', e.original_parent, isinstance(e.original_parent, GizmoArrow))

        if not LEVEL_EDITOR.selection:
            return

        changed = ( # don't record undo if transform didn't change
            distance(LEVEL_EDITOR.selection[0].world_transform[0], LEVEL_EDITOR.selection[0]._original_world_transform[0]) > .0001 or
            distance(LEVEL_EDITOR.selection[0].world_transform[1], LEVEL_EDITOR.selection[0]._original_world_transform[1]) > .0001 or
            distance(LEVEL_EDITOR.selection[0].world_transform[2], LEVEL_EDITOR.selection[0]._original_world_transform[2]) > .0001
            )

        if self.record_undo and changed:
            changes = []
            for e in LEVEL_EDITOR.selection:
                changes.append([LEVEL_EDITOR.entities.index(e), 'world_transform', e._original_world_transform, e.world_transform])

            LEVEL_EDITOR.current_scene.undo.record_undo(changes)

        self.parent = LEVEL_EDITOR.gizmo.arrow_parent
        self.position = (0,0,0)
        self.rotation = self.original_rotation
        LEVEL_EDITOR.render_selection()

    def input(self, key):
        super().input(key)
        if key == 'control':
            self.step = (1,1,1)
        elif key == 'control up':
            self.step = (0,0,0)



class Gizmo(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=LEVEL_EDITOR, enabled=False)
        self.arrow_parent = Entity(parent=self)
        self.lock_axis_helper_parent = Entity(parent=LEVEL_EDITOR,
            # model='wireframe_cube',
        )
        self.lock_axis_helper = Entity(parent=self.lock_axis_helper_parent,
            # model=Circle(6, radius=.2), color=color.red, double_sided=True, always_on_top=True, render_queue=1
        ) # this will help us lock the movement to an axis on local space


        self.subgizmos = {
            'xz' : GizmoArrow(parent=self.arrow_parent, gizmo=self, model='cube', collider='plane', scale=.6, scale_y=.05, origin=(-.75,0,-.75), color=lerp(color.magenta, color.cyan, .5), plane_direction=(0,1,0)),
            'x'  : GizmoArrow(parent=self.arrow_parent, gizmo=self, color=axis_colors['x'], lock=(0,1,1)),
            'y'  : GizmoArrow(parent=self.arrow_parent, gizmo=self, rotation=(0,0,-90), color=axis_colors['y'], lock=(1,0,1)),
            'z'  : GizmoArrow(parent=self.arrow_parent, gizmo=self, rotation=(0,-90,0), color=axis_colors['z'], plane_direction=(0,1,0), lock=(1,1,0)),
        }

        for e in self.arrow_parent.children:
            e.highlight_color = color.white
            e.original_scale = e.scale

        self.fake_gizmo = Entity(parent=LEVEL_EDITOR, enabled=False)
        self.fake_gizmo.subgizmos = dict()
        for key, value in self.subgizmos.items():
            self.fake_gizmo.subgizmos[key] = duplicate(self.subgizmos[key], parent=self.fake_gizmo, collider=None, ignore=True)


    def input(self, key):   # this will execute before GizmoArrow drag()
        if key == 'left mouse down' and mouse.hovered_entity in self.subgizmos.values():
            self.drag()

        if key == 'left mouse up' and LEVEL_EDITOR.local_global_menu.value == 'local':
            self.drop()


    def drag(self, show_gizmo_while_dragging=True):
        for i, axis in enumerate('xyz'):
            self.subgizmos[axis].plane_direction = self.up

            self.subgizmos[axis].lock = [0,0,0]
            if LEVEL_EDITOR.local_global_menu.value == 'global':
                self.subgizmos[axis].lock = [1,1,1]
                self.subgizmos[axis].lock[i] = 0

            if axis == 'y':
                self.subgizmos[axis].plane_direction = camera.back


        self.subgizmos['xz'].plane_direction = self.up
        [setattr(e, 'visible_self', show_gizmo_while_dragging) for e in self.subgizmos.values()]


        # use fake gizmo technique to lock movement to local axis. if in global mode, skip this and use the old simpler way.
        if LEVEL_EDITOR.local_global_menu.value == 'local':
            self.lock_axis_helper_parent.world_transform = self.world_transform
            self.lock_axis_helper.position = (0,0,0)
            self.fake_gizmo.world_transform = self.world_transform

            self.fake_gizmo.enabled = True
            self.visible = False
            [setattr(e, 'visible_self', show_gizmo_while_dragging) for e in self.fake_gizmo.subgizmos.values()]
            [setattr(e, 'visible_self', False) for e in self.subgizmos.values()]


    def drop(self):
        self.fake_gizmo.enabled = False
        self.visible = True
        [setattr(e, 'visible_self', False) for e in self.fake_gizmo.subgizmos.values()]
        [setattr(e, 'visible_self', True) for e in self.subgizmos.values()]
        [setattr(e, 'scale', e.original_scale) for e in self.subgizmos.values()]


    def update(self):
        if held_keys['r'] or held_keys['s']:
            return
        self.world_scale = distance(self.world_position, camera.world_position) * camera.fov * .0005

        for i, axis in enumerate('xyz'):
            if self.subgizmos[axis].dragging:
                setattr(self.lock_axis_helper, axis, self.subgizmos[axis].get_position(relative_to=self.lock_axis_helper_parent)[i])
                self.fake_gizmo.world_position = self.lock_axis_helper.world_position

        if self.subgizmos['xz'].dragging:
            self.fake_gizmo.world_position = self.subgizmos['xz'].world_position



class RotationGizmo(Entity):
    model = None

    def __init__(self, **kwargs):
        super().__init__(parent=LEVEL_EDITOR.gizmo)
        if not RotationGizmo.model:
            RotationGizmo.model = load_model('rotation_gizmo_model', application.internal_models_compressed_folder)
            if not RotationGizmo.model:
                path = Circle(24).vertices
                path.append(path[0])
                RotationGizmo.model = Pipe(base_shape=Quad(radius=0), path=[Vec3(e)*32 for e in path])
                RotationGizmo.model.save('rotation_gizmo_model.ursinamesh', application.internal_models_compressed_folder, max_decimals=4)

        self.rotator = Entity(parent=LEVEL_EDITOR.gizmo)
        self.axis = Vec3(0,1,0)
        self.subgizmos = {}
        self.sensitivity = 36000
        self.dragging = False



        for i, dir in enumerate((Vec3(-1,0,0), Vec3(0,1,0), Vec3(0,0,-1))):
            b = Button(parent=self, model=copy(RotationGizmo.model), collider='mesh',
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
        # print('drag')
        for e in LEVEL_EDITOR.selection:
            e.world_parent = self.rotator
            e._original_world_transform = e.world_transform
        self.dragging = True

    def drop(self):
        # print('drop')
        self.rotator.world_parent = LEVEL_EDITOR.gizmo
        changes = []
        for e in LEVEL_EDITOR.selection:
            e.world_parent = e.original_parent
            changes.append([LEVEL_EDITOR.entities.index(e), 'world_transform', e._original_world_transform, e.world_transform])

        LEVEL_EDITOR.current_scene.undo.record_undo(changes)
        self.dragging = False
        self.rotator.rotation = (0,0,0)
        LEVEL_EDITOR.render_selection()

    def input(self, key):
        if key == 'left mouse up' and self.dragging:
            self.dragging = False
            self.drop()


    def update(self):
        if self.dragging:
            rotation_amount = Vec3(sum(mouse.velocity), sum(mouse.velocity), sum(mouse.velocity)) * self.sensitivity * time.dt * self.axis * Vec3(1,1,-1)
            if not LEVEL_EDITOR.origin_mode_menu.value == 'individual':
                self.rotator.rotation -= rotation_amount
            else:
                for e in LEVEL_EDITOR.selection:
                    e.rotation -= rotation_amount




class ScaleGizmo(Draggable):
    def __init__(self, **kwargs):
        super().__init__(parent=LEVEL_EDITOR.gizmo, model='cube', scale=.25, color=color.orange, visible=True, always_on_top=True, render_queue=1, is_gizmo=True, dragging=False, shader=unlit_shader)
        self.scaler = Entity(parent=LEVEL_EDITOR.gizmo)
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
        for e in LEVEL_EDITOR.selection:
            e.world_parent = self.scaler
            e._original_world_transform = e.world_transform
        self.dragging = True

    def drop(self):
        changes = []
        for e in LEVEL_EDITOR.selection:
            e.world_parent = e.original_parent
            changes.append([LEVEL_EDITOR.entities.index(e), 'world_transform', e._original_world_transform, e.world_transform])

        LEVEL_EDITOR.current_scene.undo.record_undo(changes)
        self.dragging = False
        self.scaler.scale = 1
        LEVEL_EDITOR.render_selection()



    def update(self):
        if self.dragging:
            if not LEVEL_EDITOR.origin_mode_menu.value == 'individual':
                self.scaler.scale += Vec3(sum(mouse.velocity), sum(mouse.velocity), sum(mouse.velocity)) * self.sensitivity * time.dt * self.axis
            else:
                for e in LEVEL_EDITOR.selection:
                    e.scale += Vec3(sum(mouse.velocity), sum(mouse.velocity), sum(mouse.velocity)) * self.sensitivity * time.dt * self.axis

class BoxGizmo(Entity):
    def __init__(self):
        super().__init__(parent=LEVEL_EDITOR)
        self.target = None
        self.scaler = Entity(parent=self)
        self.helper = Entity(parent=self, model='cube', unlit=True, color=color.azure, enabled=False)
        self.sensitivity = 600
        self.scale_from_center = False    # scale from center if holding alt
        self.normal = None
        self.axis_name = None

    def input(self, key):
        if key == 'a':
            [setattr(e, 'collision', True) for e in LEVEL_EDITOR.entities]
            mouse.update()

            if mouse.hovered_entity in LEVEL_EDITOR.entities and mouse.normal and mouse.normal != Vec3(0):
                self.target = mouse.hovered_entity
                self.target._original_world_transform = self.target.world_transform
                # self.target.original_parent = self.target.parent

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

                LEVEL_EDITOR.local_global_menu.original_value = LEVEL_EDITOR.local_global_menu.value
                if not LEVEL_EDITOR.local_global_menu.value == 'local':
                    LEVEL_EDITOR.local_global_menu.value = 'local'

                LEVEL_EDITOR.selection = [self.helper, ]
                LEVEL_EDITOR.render_selection()
                LEVEL_EDITOR.gizmo.enabled = True
                LEVEL_EDITOR.gizmo.drag(show_gizmo_while_dragging=False)
                LEVEL_EDITOR.gizmo.subgizmos[self.axis_name].start_dragging()


        elif key == 'a up' and self.target:
            [setattr(e, 'collision', False) for e in LEVEL_EDITOR.entities]
            self.target.world_parent = self.target.original_parent
            self.normal = None
            self.helper.parent = self
            self.scaler.scale = 1

            LEVEL_EDITOR.gizmo.drop()
            LEVEL_EDITOR.gizmo.subgizmos[self.axis_name].record_undo = False
            LEVEL_EDITOR.gizmo.subgizmos[self.axis_name].stop_dragging()
            LEVEL_EDITOR.gizmo.subgizmos[self.axis_name].record_undo = True
            LEVEL_EDITOR.selection = []
            LEVEL_EDITOR.local_global_menu.value = LEVEL_EDITOR.local_global_menu.original_value
            LEVEL_EDITOR.gizmo.enabled = False
            self.helper.enabled = False

            LEVEL_EDITOR.current_scene.undo.record_undo([(LEVEL_EDITOR.entities.index(self.target), 'world_transform', self.target._original_world_transform, self.target.world_transform), ])
            self.target = None


    def update(self):
        if self.target and held_keys['a'] and self.helper and self.scaler:
            relative_position = self.helper.get_position(relative_to=self.scaler)
            value = abs(relative_position[[abs(int(e)) for e in self.normal].index(1)])
            if self.scale_from_center:
                value *= 2

            setattr(self.target, f'scale_{self.axis_name}', value)

            if not self.scale_from_center:
                self.target.world_position = lerp(self.scaler.world_position, self.helper.world_position, .5)




class GizmoToggler(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=LEVEL_EDITOR)
        self.animator = Animator({
            'w' : LEVEL_EDITOR.gizmo.arrow_parent,
            'e' : LEVEL_EDITOR.scale_gizmo,
            'u' : LEVEL_EDITOR.rotation_gizmo,
            # 't' : box_gizmo,

            'q' : None,
        })

    def input(self, key):
        key = input_handler.get_combined_key(key)

        if key in self.animator.animations and not mouse.left:
            self.animator.state = key


class QuickGrabber(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=LEVEL_EDITOR)
        self.target_entity = None
        self.target_axis = None
        self.plane = Entity(model='quad', collider='box', scale=Vec3(999,999,1), visible_self=False, enabled=False)
        self.offset_helper = Entity()
        self.start_position = Vec3(0,0,0)
        self.axis_lock = [0,1,0]
        self.is_dragging = False
        self.shortcuts = {
            'left mouse down': Func(self.start_moving_on_axis, 'xz'),
            'd': Func(self.start_moving_on_axis, 'xz'),
            'w': Func(self.start_moving_on_axis, 'xz', auto_select_hovered_entity=False),
            'x': Func(self.start_moving_on_axis, 'x'),
            'y': Func(self.start_moving_on_axis, 'y'),
            'z': Func(self.start_moving_on_axis, 'z'),
            }

    def start_moving_on_axis(self, axis, auto_select_hovered_entity=True):
        if not auto_select_hovered_entity and len(LEVEL_EDITOR.selection) > 1:
            return

        self.target_entity = LEVEL_EDITOR.selector.get_hovered_entity()
        LEVEL_EDITOR.gizmo.enabled = False
        # print('MOVE ON AXIS', axis)
        if self.target_entity:
            LEVEL_EDITOR.selection = [self.target_entity, ]
            self.plane.enabled = True
            self.plane.position = self.target_entity.world_position

            if axis == 'y' or axis == 'xy':
                self.plane.look_at(self.plane.position + Vec3(0,0,-1))
            else:
                self.plane.look_at(self.plane.position + Vec3(0,1,0))

            if len(axis) > 1:
                self.axis_lock = [0,0,0]
            else:
                self.axis_lock = [axis!='x', axis!='y', axis!='z']

            mouse.traverse_target = self.plane
            mouse.update()
            self.offset_helper.position = mouse.world_point
            self.start_position = self.offset_helper.world_position

            if not hasattr(self.target_entity.parent, 'is_gizmo') or self.target_entity.parent.is_gizmo == False:
                self.target_entity.original_parent = self.target_entity.parent
            else:
                self.target_entity.original_parent = scene

            self.target_entity._original_world_position = self.target_entity.world_position
            self.target_entity.world_parent = self.offset_helper

            self.is_dragging = True


    def input(self, key):
        combined_key = input_handler.get_combined_key(key)

        if not key.endswith(' up') and (held_keys['shift'] or held_keys['alt'] or held_keys['s'] or mouse.right or mouse.middle or held_keys['r']):
            return

        if combined_key == 'left mouse up' and self.target_entity and distance(self.target_entity._original_world_position, self.target_entity.world_position) < .1 and (time.time()-mouse.prev_click_time) < .5:  # prevent accidentally moving the entity when you meant to select it
            self.is_dragging = False
            mouse.traverse_target = scene
            self.target_entity.world_parent = self.target_entity.original_parent
            self.target_entity.world_position = self.target_entity._original_world_position
            LEVEL_EDITOR.selection = [self.target_entity, ]
            LEVEL_EDITOR.render_selection()
            self.target_entity = None
            self.plane.enabled = False
            return

        if combined_key in self.shortcuts.keys():
            if self.target_entity:
                return
            self.shortcuts[key]()

        elif (key in [f'{e} up' for e in self.shortcuts.keys()] or 'left mouse down' in self.shortcuts and key == 'left mouse up') and self.target_entity:
            self.drop()


    def drop(self):
        self.is_dragging = False
        mouse.traverse_target = scene
        self.target_entity.world_parent = self.target_entity.original_parent

        if self.target_entity.world_position != self.target_entity._original_world_position:
            changes = []
            for e in LEVEL_EDITOR.selection:
                changes.append([LEVEL_EDITOR.entities.index(e), 'world_position', e._original_world_position, e.world_position])

            LEVEL_EDITOR.current_scene.undo.record_undo(changes)
            LEVEL_EDITOR.selection = []
            LEVEL_EDITOR.render_selection()
        else:
            LEVEL_EDITOR.selection = [self.target_entity, ]
            LEVEL_EDITOR.render_selection()

        self.target_entity = None
        self.plane.enabled = False


    def on_disable(self):
        self.drop()


    def update(self):
        if not self.is_dragging or not mouse.world_point:
            return

        if mouse.right:
            return

        pos = mouse.world_point
        if held_keys['control']:
            pos = round(pos)

        for i, e in enumerate(pos):
            if self.axis_lock[i]:
                pos[i] = self.start_position[i]

        self.offset_helper.world_position = pos
        if held_keys['control']:
            snap_step = 1
            self.offset_helper.world_position = Vec3(*[round(e * snap_step) /snap_step for e in self.offset_helper.world_position])
            self.target_entity.world_position = Vec3(*[round(e * snap_step) /snap_step for e in self.target_entity.world_position])


class QuickScaler(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=LEVEL_EDITOR,
            gizmos_to_toggle={
                's' :  LEVEL_EDITOR.scale_gizmo,
                'sx' : LEVEL_EDITOR.scale_gizmo,
                'sy' : LEVEL_EDITOR.scale_gizmo,
                'sz' : LEVEL_EDITOR.scale_gizmo,
            },
            clear_selection=False,
            dragging=False,
            original_gizmo_state='q'
            )


    def input(self, key):
        if held_keys['control'] or held_keys['shift'] or held_keys['alt'] or mouse.left or mouse.middle or held_keys['r'] or held_keys['d'] or held_keys['t']:
            return

        if (held_keys['x'] or held_keys['y'] or held_keys['z']) and key == 's':
            self.original_gizmo_state = LEVEL_EDITOR.gizmo_toggler.animator.state
            return

        if held_keys['s'] and key in 'xyz':
            key = 's' + key

        if key in ('s', 'sx', 'sy', 'sz'):
            self.original_gizmo_state = LEVEL_EDITOR.gizmo_toggler.animator.state
            LEVEL_EDITOR.gizmo_toggler.animator.state = 'e'

            if not key == 's':
                LEVEL_EDITOR.scale_gizmo.axis = (Vec3(1,0,0), Vec3(0,1,0), Vec3(0,0,1))[('sx', 'sy', 'sz').index(key)]


        if key in self.gizmos_to_toggle.keys():
            LEVEL_EDITOR.selector.enabled = False
            LEVEL_EDITOR.selection_box.enabled = False

            LEVEL_EDITOR.gizmo.arrow_parent.visible = False
            LEVEL_EDITOR.scale_gizmo.visible = False
            self.gizmos_to_toggle[key].visible_self = False
            if not key in ('sx', 'sy', 'sz'):
                self.clear_selection = not LEVEL_EDITOR.selection

            if not LEVEL_EDITOR.selection:
                LEVEL_EDITOR.selector.input('left mouse down')

            self.gizmos_to_toggle[key].input('left mouse down')
            self.gizmos_to_toggle[key].start_dragging()


        # print('------------', key)
        if key in ('s up', 'x up', 'y up', 'z up'):
            for e in self.gizmos_to_toggle.values():
                e.input('left mouse up')
            # self.gizmos_to_toggle[key].drop()
            if self.clear_selection:
                LEVEL_EDITOR.selection.clear()
                LEVEL_EDITOR.render_selection()

            LEVEL_EDITOR.gizmo.arrow_parent.visible = True
            LEVEL_EDITOR.scale_gizmo.visible = True
            LEVEL_EDITOR.scale_gizmo.axis = Vec3(1,1,1)
            # self.gizmos_to_toggle[key].visible_self = True
            LEVEL_EDITOR.gizmo_toggler.animator.state = self.original_gizmo_state

            LEVEL_EDITOR.selector.enabled = True
            LEVEL_EDITOR.selection_box.enabled = True
            mouse.traverse_target = scene


    def update(self):
        for key in self.gizmos_to_toggle.keys():
            if held_keys[key] and not held_keys['control'] and not held_keys['shift'] and mouse.velocity != Vec3(0,0,0):
                LEVEL_EDITOR.render_selection(update_gizmo_position=False)
                return


class QuickRotator(Entity):
    def __init__(self):
        super().__init__(parent=LEVEL_EDITOR)

    def input(self, key):
        if held_keys['control'] or held_keys['shift'] or held_keys['alt'] or held_keys['s']:
            return

        if key == 'r' and len(LEVEL_EDITOR.selection) <= 1:
            if not LEVEL_EDITOR.selection:
                LEVEL_EDITOR.selection = [LEVEL_EDITOR.selector.get_hovered_entity(), ]
                LEVEL_EDITOR.render_selection()

            if not LEVEL_EDITOR.selection:
                return

            self.target_entity = LEVEL_EDITOR.selection[0]
            LEVEL_EDITOR.rotation_gizmo.subgizmos['y'].input('left mouse down')
            LEVEL_EDITOR.rotation_gizmo.subgizmos['y'].start_dragging()

        elif key == 'r up' and hasattr(self, 'target_entity') and self.target_entity:
            key = key[:-3]
            LEVEL_EDITOR.rotation_gizmo.subgizmos['y'].input('left mouse up')
            LEVEL_EDITOR.rotation_gizmo.subgizmos['y'].drop()
            LEVEL_EDITOR.selection.clear()
            LEVEL_EDITOR.render_selection()
            self.target_entity = None

    def update(self):
        if held_keys['r'] and not held_keys['control'] and not held_keys['shift'] and mouse.velocity != Vec3(0,0,0):
            LEVEL_EDITOR.render_selection(update_gizmo_position=False)
            return


class RotateRelativeToView(Entity):
    _rotation_helper = Entity(name='RotateRelativeToView_rotation_helper', add_to_scene_entities=False)
    sensitivity = Vec2(200,200)

    def __init__(self, **kwargs):
        super().__init__(parent=LEVEL_EDITOR, **kwargs)

    def input(self, key):
        if held_keys['control'] or held_keys['shift'] or held_keys['alt'] or held_keys['s'] or held_keys['r']:
            return

        if key == 't':
            if len(LEVEL_EDITOR.selection) > 1:
                return

            if not LEVEL_EDITOR.selection:
                LEVEL_EDITOR.selection = [LEVEL_EDITOR.selector.get_hovered_entity(), ]
                LEVEL_EDITOR.render_selection()

            if not LEVEL_EDITOR.selection:
                return

            self.target_entity = LEVEL_EDITOR.selection[0]
            __class__._rotation_helper.world_parent = scene
            __class__._rotation_helper.position = self.target_entity.world_position
            __class__._rotation_helper.rotation = Vec3(0,0,0)

            self._entity_original_parent = self.target_entity.parent
            self._entity_original_rotation = self.target_entity.world_rotation
            self.target_entity.world_parent = __class__._rotation_helper
            self._mouse_start_x = mouse.x
            self._mouse_start_y = mouse.y

        elif key == 't up' and self.target_entity:
            self.target_entity.world_parent = self._entity_original_parent
            LEVEL_EDITOR.selection.clear()
            LEVEL_EDITOR.render_selection()
            self.target_entity = None
            self.x_mov = 0
            self.y_mov = 0

    def update(self):
        if self.target_entity and held_keys['t']:
            __class__._rotation_helper.rotation_y -= mouse.velocity[0] * __class__.sensitivity.x / camera.aspect_ratio
            __class__._rotation_helper.rotation_x += mouse.velocity[1] * __class__.sensitivity.y




class Selector(Entity):
    def __init__(self):
        super().__init__(parent=LEVEL_EDITOR)

    def input(self, key):
        if key == 'left mouse down':
            if mouse.hovered_entity:
                # print('sroifjseofisjeoij')
                return

            clicked_entity = self.get_hovered_entity()

            if clicked_entity in LEVEL_EDITOR.entities and not held_keys['alt']:
                if held_keys['shift']:
                    if not clicked_entity in LEVEL_EDITOR.selection:
                        LEVEL_EDITOR.selection.append(clicked_entity) # append
                else:
                    LEVEL_EDITOR.selection = [clicked_entity, ]   # overwrite

            if held_keys['alt'] and clicked_entity in LEVEL_EDITOR.selection:
                LEVEL_EDITOR.selection.remove(clicked_entity) # remove

            if not clicked_entity and not held_keys['shift'] and not held_keys['alt']: # clear
                LEVEL_EDITOR.selection.clear()

            LEVEL_EDITOR.render_selection()

        if held_keys['control'] and key == 'a':
            LEVEL_EDITOR.selection = [e for e in LEVEL_EDITOR.entities]
            LEVEL_EDITOR.render_selection()

        elif key == 'h':
            LEVEL_EDITOR.point_renderer.enabled = not LEVEL_EDITOR.point_renderer.enabled

        if key == 'left mouse up':
            LEVEL_EDITOR.gizmo.enabled = bool(LEVEL_EDITOR.selection)



    def get_hovered_entity(self):
        LEVEL_EDITOR.entities = [e for e in LEVEL_EDITOR.entities if e]
        # [print(str(e)) for e in LEVEL_EDITOR.entities]
        entities_in_range = [(distance_2d(e.screen_position, mouse.position), e) for e in LEVEL_EDITOR.entities if e and e.selectable and not e.collider]
        entities_in_range = [e for e in entities_in_range if e[0] < .03]
        entities_in_range.sort()

        clicked_entity = None
        if entities_in_range:
            return entities_in_range[0][1]

        # try getting entities with box collider
        [setattr(e, 'collision', True) for e in LEVEL_EDITOR.entities if not hasattr(e, 'is_gizmo')]
        # print('-------------', len([e for e in LEVEL_EDITOR.entities  if not hasattr(e, 'is_gizmo') and e.collider and e.collision]))
        mouse.update()

        if mouse.hovered_entity in LEVEL_EDITOR.entities:

            [setattr(e, 'collision', False) for e in LEVEL_EDITOR.entities if not hasattr(e, 'is_gizmo')]
            return mouse.hovered_entity

        [setattr(e, 'collision', False) for e in LEVEL_EDITOR.entities if not hasattr(e, 'is_gizmo')]



class SelectionBox(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=LEVEL_EDITOR.ui, visible=False, **kwargs)

    def input(self, key):
        if key == 'left mouse down':
            if mouse.hovered_entity and mouse.hovered_entity not in LEVEL_EDITOR.selection:
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
                LEVEL_EDITOR.selection.clear()

            for e in LEVEL_EDITOR.entities:
                if not e.selectable:
                    continue

                pos = e.screen_position
                if pos.x > self.x and pos.x < self.x + abs(self.scale_x) and pos.y > self.y and pos.y < self.y + abs(self.scale_y):
                    if self.mode in ('add', 'new') and not e in LEVEL_EDITOR.selection:
                        LEVEL_EDITOR.selection.append(e)
                    elif self.mode == 'subtract' and e in LEVEL_EDITOR.selection:
                        LEVEL_EDITOR.selection.remove(e)

            LEVEL_EDITOR.render_selection()
            self.mode = 'new'

    def update(self):
        if mouse.left:
            if mouse.x == mouse.start_x and mouse.y == mouse.start_y:
                return

            self.scale_x = mouse.x - self.x
            self.scale_y = mouse.y - self.y




class WhiteCube(Entity):
    default_values = Entity.default_values | dict(model='cube', shader='lit_with_shadows_shader', texture='white_cube', collider='box', name='cube') # combine dicts
    def __init__(self, **kwargs):
        super().__init__(**__class__.default_values | kwargs)

    def __deepcopy__(self, memo):
        return eval(repr(self))


class ClassSpawner(Entity):
    default_values = Entity.default_values | dict(class_to_spawn='', model='wireframe_cube', color=color.blue, name='ClassSpawner') # combine dicts
    '''Prefab for spawning target class on play'''
    def __init__(self, **kwargs):
        super().__init__(**__class__.default_values | kwargs)
        self.class_instance = None

    def draw_inspector(self):
        return {'class_to_spawn': type}

    def start(self):
        self.enabled = False
        if self.class_to_spawn not in LEVEL_EDITOR.class_menu.available_classes:
            print_warning('class to spawn not found in LEVEL_EDITOR.class_menu.available_classes:', self.class_to_spawn)
            return

        if self.class_to_spawn:
            print('spawn class', self.class_to_spawn)
            self.class_instance = LEVEL_EDITOR.class_menu.available_classes[self.class_to_spawn](world_transform=self.world_transform, add_to_scene_entities=False)

    def stop(self):
        if self.class_instance:
            destroy(self.class_instance)
            self.class_instance = None
        self.enabled = True

    def __deepcopy__(self, memo):
        return eval(repr(self))


class TriplanarCube(Entity):
    default_values = Entity.default_values | dict(model='cube', shader='triplanar_shader', texture='white_cube', collider='box', name='cube') # combine dicts

    def __init__(self, **kwargs):
        super().__init__(**__class__.default_values | kwargs)
        self.set_shader_input('side_texture', load_texture('brick'))

    def __deepcopy__(self, memo):
        return eval(repr(self))


class Pyramid(Entity):
    default_values = Entity.default_values | dict(name='pyramid', model=Cone(4), texture='brick') # combine dicts

    def __init__(self, **kwargs):
        super().__init__(**__class__.default_values | kwargs)

    def __deepcopy__(self, memo):
        return eval(repr(self))


class Rock(Entity):
    default_values = Entity.default_values | dict(name='rock', model='procedural_rock_0', collider='box', color=hsv(20,.2,.45)) # combine dicts
    gizmo_color = color.brown
    def __init__(self, **kwargs):
        super().__init__(**__class__.default_values | kwargs)

    def __deepcopy__(self, memo):
        return eval(repr(self))


class Spawner(Entity):
    def __init__(self):
        super().__init__(parent=LEVEL_EDITOR)
        self.target = None
        self.ui = Entity(parent=LEVEL_EDITOR.ui, position=window.bottom)
        self.update_menu()

    def update_menu(self):
        [destroy(e) for e in self.ui.children]
        # for file in LEVEL_EDITOR.prefab_folder.glob('**/*.py')
        import_all_classes(LEVEL_EDITOR.prefab_folder, debug=True)
        # LEVEL_EDITOR.prefabs =

        for i, prefab in enumerate(LEVEL_EDITOR.built_in_prefabs + LEVEL_EDITOR.prefabs):
            button = Button(parent=self.ui, scale=.075/2, text=' ', text_size=.5, on_click=Func(self.spawn_entity, prefab))
            if hasattr(prefab, 'icon'):
                button.icon = prefab.icon
            else:
                button.text = '\n'.join(chunk_list(prefab.__name__, 5))

        grid_layout(self.ui.children, origin=(0,-.5), spacing=(.05,0,0), max_x=32)



    def input(self, key):
        if key == 'i':
            mouse.traverse_target = LEVEL_EDITOR.grid
            self.spawn_entity()

        elif key == 'i up' and self.target:
            self.drop_entity()
            mouse.traverse_target = scene

        elif self.target and key == 'left mouse up':
            self.drop_entity()

    def spawn_entity(self, _class=Entity):
        if not LEVEL_EDITOR.current_scene:
            print_on_screen('<red>select a scene first', position=(0,0), origin=(0,0))
            return

        LEVEL_EDITOR.grid.enabled = True
        self.target = _class(position=mouse.world_point, original_parent=LEVEL_EDITOR, selectable=True, collision=False)
        if not hasattr(self.target, 'collider_type'):
            self.target.collider_type = 'None'
        # print(self.target.model.name)
        # if not self.target.collider:
        #     self.target.collider = 'box'
        #     self.target.collision = False
        if not self.target.shader:
            self.target.shader = lit_with_shadows_shader

        LEVEL_EDITOR.current_scene.entities.append(self.target)
        LEVEL_EDITOR.render_selection()


    def drop_entity(self):
        LEVEL_EDITOR.current_scene.undo.record_undo(('delete entities', [LEVEL_EDITOR.current_scene.entities.index(self.target), ], [repr(self.target), ]))
        LEVEL_EDITOR.selection = [self.target, ]
        self.target = None
        LEVEL_EDITOR.grid.enabled = False


    def update(self):
        if mouse.world_point and self.target:
            if held_keys['n'] or mouse.left:
                self.target.position = mouse.world_point


class Deleter(Entity):
    def __init__(self):
        super().__init__(parent=LEVEL_EDITOR)
        self.shortcuts = ['delete', 'control+x']

    def input(self, key):
        combined_key = input_handler.get_combined_key(key)
        if LEVEL_EDITOR.selection and combined_key in self.shortcuts:
            self.delete_selected()

    def delete_selected(self):
        LEVEL_EDITOR.current_scene.undo.record_undo((
            'restore entities',
            [LEVEL_EDITOR.entities.index(e) for e in LEVEL_EDITOR.selection],
            [repr(e) for e in LEVEL_EDITOR.selection],
            ))

        # print(LEVEL_EDITOR.selection)
        before = len(LEVEL_EDITOR.entities)
        # LEVEL_EDITOR.entities = [e for e in LEVEL_EDITOR.entities if e not in LEVEL_EDITOR.selection]
        for e in LEVEL_EDITOR.selection:
            if e in LEVEL_EDITOR.entities:
                LEVEL_EDITOR.entities.remove(e)

        # print('---------------', before, '-->', len(LEVEL_EDITOR.entities))
        [setattr(e, 'parent', LEVEL_EDITOR) for e in LEVEL_EDITOR.cubes]
        [destroy(e) for e in LEVEL_EDITOR.selection]
        LEVEL_EDITOR.selection.clear()
        LEVEL_EDITOR.render_selection()


class Grouper(Entity):
    def __init__(self):
        super().__init__(parent=LEVEL_EDITOR)

    def input(self, key):
        if held_keys['control'] and key == 'g' and LEVEL_EDITOR.selection:
            group_entity = Entity(parent=LEVEL_EDITOR.current_scene.scene_parent, name='[group]', selectable=True)
            LEVEL_EDITOR.entities.append(group_entity)

            parents = tuple(set([e.parent for e in LEVEL_EDITOR.selection]))
            if len(parents) == 1:
                group_entity.world_parent = parents[0]

            group_entity.world_position = sum([e.world_position for e in LEVEL_EDITOR.selection]) / len(LEVEL_EDITOR.selection)
            for e in LEVEL_EDITOR.selection:
                e.world_parent = group_entity

            LEVEL_EDITOR.selection = [group_entity, ]
            LEVEL_EDITOR.render_selection()



class PointOfViewSelector(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=LEVEL_EDITOR.ui, model='cube', collider='box', texture='white_cube', scale=.05, position=window.top_right-Vec2(.1,.05))
        self.front_text = Text(parent=self, text='front', z=-.5, scale=10, origin=(0,0), color=color.azure)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def on_click(self):
        if mouse.normal == Vec3(0,0,-1):   LEVEL_EDITOR.editor_camera.animate_rotation((0,0,0)) # front
        elif mouse.normal == Vec3(0,0,1):  LEVEL_EDITOR.editor_camera.animate_rotation((0,180,0)) # back
        elif mouse.normal == Vec3(1,0,0):  LEVEL_EDITOR.editor_camera.animate_rotation((0,90,0)) # right
        elif mouse.normal == Vec3(-1,0,0): LEVEL_EDITOR.editor_camera.animate_rotation((0,-90,0)) # right
        elif mouse.normal == Vec3(0,1,0):  LEVEL_EDITOR.editor_camera.animate_rotation((90,0,0)) # top
        elif mouse.normal == Vec3(0,-1,0): LEVEL_EDITOR.editor_camera.animate_rotation((-90,0,0)) # top


    def update(self):
        self.rotation = -LEVEL_EDITOR.editor_camera.rotation

    def input(self, key):
        if held_keys['shift']:
            if key == '1':   LEVEL_EDITOR.editor_camera.animate_rotation((0,0,0)) # front
            elif key == '3': LEVEL_EDITOR.editor_camera.animate_rotation((0,90,0)) # right
            elif key == '7': LEVEL_EDITOR.editor_camera.animate_rotation((90,0,0)) # top
            elif key == '5': camera.orthographic = not camera.orthographic


# class PaintBucket(Entity):
#     def input(self, key):
#         if held_keys['alt'] and key == 'c' and mouse.hovered_entity:
#             self.color = mouse.hovered_entity.color

class Copier(Entity):
    prefix = 'ursina_editor_copy_data:```py\n'

    def input(self, key):
        if held_keys['control'] and key == 'c':
            if LEVEL_EDITOR.selection:
                code = __class__.prefix
                for e in LEVEL_EDITOR.selection:
                    entity_repr = repr(e)
                    if not 'collider_type=' in entity_repr and hasattr(e, 'collider_type'):
                        entity_repr = f'{entity_repr[:-1]}collider_type=\'{e.collider_type}\')'
                    code += entity_repr + '\n'

                pyperclip.copy(f'{code}\n```')

        if held_keys['control'] and key == 'v':
            value = pyperclip.paste()
            if value.startswith('ursina_editor_copy_data:```py\n') and value.endswith('\n```'):
                cleaned_code = value[len(__class__.prefix):-4].strip().split('\n')
                clones = []
                for line in cleaned_code:
                    instance = eval(line)
                    instance.selectable = True
                    LEVEL_EDITOR.current_scene.entities.append(instance)
                    clones.append(instance)

                LEVEL_EDITOR.entities.extend(clones)
                LEVEL_EDITOR.selection = clones
                LEVEL_EDITOR.current_scene.undo.record_undo(('delete entities', [LEVEL_EDITOR.entities.index(en) for en in clones], [repr(e) for e in clones]))
                print('------------------------')
                LEVEL_EDITOR.render_selection()




class LevelMenu(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=LEVEL_EDITOR)
        self.menu = Entity(parent=LEVEL_EDITOR.ui, model=Quad(radius=.05), color=color.black, scale=.2, origin=(.5,0), x=camera.aspect_ratio*.495, y=-.3, collider='box')
        self.menu.grid = Entity(parent=self.menu, model=Grid(8,8), z=-1, origin=self.menu.origin, color=color.dark_gray)
        self.content_renderer = Entity(parent=self.menu, scale=1/8, position=(-1,-.5,-1), model=Mesh(), color='#222222') # scales the content so I can set the position as (x,y) instead of (-1+(x/8),-.5+(y/8))
        self.cursor = Entity(parent=self.content_renderer, model='quad', color=color.lime, origin=(-.5,-.5), z=-2, alpha=.5)
        self.current_scene_indicator = Entity(parent=self.content_renderer, model='circle', color=color.azure, origin=(-.5,-.5), z=-1, enabled=False)
        # self.tabs = [Button(parent=self.menu, scale=(1/4,1/8), position=(-1+(i/4),.5), origin=(-.5,-.5), color=color.hsv(90*i,.5,.3)) for i in range(4)]


        self.current_scene_label = Text(parent=self.menu, x=-1, y=-.5, text='current scene:', z=-10, scale=2.5)

        self.load_scenes()
        # self.goto_scene(0, 0)
        self.draw()


    def load_scenes(self):
        for scene_file in LEVEL_EDITOR.scene_folder.glob('*.csv'):
            if '__' in scene_file.name:
                continue

            # print('found scene:', scene_file)
            name = scene_file.stem
            if '[' in name and ']' in name:
                x, y = (int(e) for e in name.split('[')[1].split(']')[0].split(','))
                # print('scene is at coordinate:', x, y)
                LEVEL_EDITOR.scenes[x][y].path = scene_file


    def draw(self):
        if not hasattr(self, 'quad_vertices'):
            self.quad_vertices = load_model('quad', application.internal_models_compressed_folder, use_deepcopy=True).vertices
            self.quad_vertices = [Vec3(*e)*.75 for e in self.quad_vertices]

        self.content_renderer.model.clear()
        for x in range(8):
            for y in range(8):
                if LEVEL_EDITOR.scenes[x][y].path:
                    self.content_renderer.model.vertices += [Vec3(*v)+Vec3(x+.5,y+.5,0) for v in self.quad_vertices]

        self.content_renderer.model.generate()


    def update(self):
        self.cursor.enabled = self.menu.hovered
        if self.menu.hovered:
            grid_pos = [floor((mouse.point.x+1) * 8), floor((mouse.point.y+.5) * 8)]
            self.cursor.position = grid_pos


    def input(self, key):
        combined_key = input_handler.get_combined_key(key)
        if combined_key == 'shift+m':
            self.menu.enabled = not self.menu.enabled

        # if key == 'left mouse down' and self.menu.hovered:
        #     self.click_start_pos = [int((mouse.point.x+1) * 8), int((mouse.point.y+.5) * 8)]

        if key == 'left mouse down' and self.menu.hovered:
            x, y = [int((mouse.point.x+1) * 8), int((mouse.point.y+.5) * 8)]
            # start_x, start_y = self.click_start_pos
            #
            # if x != start_x or y != start_y: # move scene
            #     print(f'move scene at {start_x},{start_y} to {x},{y}')
            #     scene_a = LEVEL_EDITOR.scenes[start_x][start_y]
            #     scene_a.coordinates = (x,y)
            #     scene_a.name = scene_a.name.split('[')[0] + f'[{x},{y}]'
            #     if scene_a.path:
            #         scene_a.path = scene_a.path.parent / (scene_a.name + '.py')
            #
            #     scene_b = LEVEL_EDITOR.scenes[x][y]
            #     scene_b.coordinates = (start_x, start_y)
            #     scene_b.name = scene_a.name.split('[')[0] + f'[{start_x},{start_y}]'
            #     if scene_b.path:
            #         scene_b.path = scene_b.path.parent / (scene_b.name + '.py')
            #
            #     # swap scenes
            #     LEVEL_EDITOR.scenes[self.click_start_pos[0]][self.click_start_pos[1]], LEVEL_EDITOR.scenes[x][y] = LEVEL_EDITOR.scenes[x][y], LEVEL_EDITOR.scenes[self.click_start_pos[0]][self.click_start_pos[1]]
            #
            #     self.draw()
            #     return
            # print(x, y)
            if not held_keys['shift'] and not held_keys['alt']:
                self.goto_scene(x, y)

            elif held_keys['shift'] and not held_keys['alt']: # append
                LEVEL_EDITOR.scenes[x][y].load()

            elif held_keys['alt'] and not held_keys['shift']: # remove
                LEVEL_EDITOR.scenes[x][y].unload()


        # hotkeys for loading neighbour levels
        if held_keys['shift'] and held_keys['alt'] and key in 'wasd':
            if not LEVEL_EDITOR.current_scene:
                return

            coords = copy(LEVEL_EDITOR.current_scene.coordinates)

            if key == 'd': coords[0] += 1
            if key == 'a': coords[0] -= 1
            if key == 'w': coords[1] += 1
            if key == 's': coords[1] -= 1

            # print(LEVEL_EDITOR.current_scene.coordinates, '-->', coords)
            coords[0] = clamp(coords[0], 0, 8)
            coords[1] = clamp(coords[1], 0, 8)
            self.goto_scene(coords[0], coords[1])


        # elif key == 'right mouse down' and self.hovered:
        #     x, y = [int((mouse.point.x+1) * 8), int((mouse.point.y+.5) * 8)]
        #     self.right_click_menu.enabled = True
        #     self.right_click_menu.position = (x,y)



    def goto_scene(self, x, y):
        self.current_scene_indicator.enabled = True
        self.current_scene_indicator.position = (x,y)
        [[LEVEL_EDITOR.scenes[_x][_y].unload() for _x in range(8)] for _y in range(8)]
        LEVEL_EDITOR.current_scene = LEVEL_EDITOR.scenes[x][y]
        LEVEL_EDITOR.current_scene.load()
        self.current_scene_label.text = LEVEL_EDITOR.current_scene.name
        self.draw()
        LEVEL_EDITOR.render_selection()

        LEVEL_EDITOR.inspector.update_inspector()
        if LEVEL_EDITOR.current_scene.scene_parent:
            LEVEL_EDITOR.sun_handler.update_bounds(LEVEL_EDITOR.current_scene.scene_parent)


class HierarchyList(Entity):
    def __init__(self):
        super().__init__(parent=LEVEL_EDITOR.ui)
        self.quad_model = load_model('quad', application.internal_models_folder, use_deepcopy=True)
        self.bg = Entity(parent=self, model='quad', collider='box', origin=(-.5,.5), color=color.black90, position=window.top_left+Vec2(0,-.05), scale=(.15,10))
        self.entity_list_text = Text(font='VeraMono.ttf', parent=self, scale=.6, line_height=1, position=window.top_left+Vec2(.005,-.05), z=-2)
        self.selected_renderer = Entity(parent=self.entity_list_text, scale=(.25,Text.size), model=Mesh(vertices=[]), color=hsv(210,.9,.6), origin=(-.5,.5), x=-.01, z=-1)
        self.selected_renderer.world_parent = self
        self.selected_renderer.z= -.1
        self.prev_y = None
        self.i = 0

    def input(self, key):
        if key == 'left mouse down' and self.bg.hovered:
            y = int(-mouse.point.y * self.bg.scale_y / Text.size / self.entity_list_text.scale_y)
            if y < len(LEVEL_EDITOR.entities):
                if not held_keys['control'] and not held_keys['shift']:     # select one
                    LEVEL_EDITOR.selection = [LEVEL_EDITOR.entities[self.entity_indices[y]], ]
                elif held_keys['control'] and not held_keys['shift']:       # add one
                    LEVEL_EDITOR.selection.append(LEVEL_EDITOR.entities[self.entity_indices[y]])
                elif held_keys['shift'] and self.prev_y:                    # add multiple
                    from_y = min(self.prev_y, y)
                    to_y = max(self.prev_y, y)
                    for _ in range(from_y, to_y+1):
                        LEVEL_EDITOR.selection.append(LEVEL_EDITOR.entities[self.entity_indices[_]])

            elif not held_keys['control'] and not held_keys['shift']:
                LEVEL_EDITOR.selection.clear()

            self.prev_y = y
            LEVEL_EDITOR.render_selection()
            # LEVEL_EDITOR.render_selection()


        if key == 'left mouse up':
            LEVEL_EDITOR.render_selection()


    def draw(self, entity, indent=0):
        self.entity_indices[self.i] = LEVEL_EDITOR.entities.index(entity)
        if not entity in LEVEL_EDITOR.selection:
            self._text += f'<gray>{" "*indent}{entity.name if entity.name else "lol"}\n'
        else:
            self.selected_renderer.model.vertices.extend([Vec3(v)-Vec3(0,self.i,0) for v in self.quad_model.vertices])
            self._text += f'<white>{" "*indent}{entity.name}\n'

        self.i += 1


    def render_selection(self):
        self._text = ''
        self.selected_renderer.model.vertices = []
        self.entity_indices = [-1 for e in LEVEL_EDITOR.entities]

        self.i = 0
        current_node = None

        for entity in LEVEL_EDITOR.entities:
            if hasattr(entity, 'is_gizmo') and entity.is_gizmo:
                continue

            if entity.parent == LEVEL_EDITOR.current_scene.scene_parent:
                self.draw(entity, indent=0)

                for child in [e for e in entity.children if e in LEVEL_EDITOR.entities]:
                    if hasattr(child, 'is_gizmo') and child.is_gizmo:
                        continue
                    self.draw(child, indent=1)

                    for child_2 in [e for e in child.children if e in LEVEL_EDITOR.entities]:
                        if hasattr(child_2, 'is_gizmo') and child_2.is_gizmo:
                            continue
                        self.draw(child_2, indent=2)

                        for child_3 in [e for e in child_2.children if e in LEVEL_EDITOR.entities]:
                            if hasattr(child_3, 'is_gizmo') and child_3.is_gizmo:
                                continue
                            self.draw(child_3, indent=3)


        self.entity_list_text.text = self._text
        self.selected_renderer.model.generate()


Text.default_font = 'VeraMono.ttf'
class InspectorInputField(InputField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text_field.x = .05
        self.text_field.y = -.25
        self.text_field.world_scale = 25 * .75
        self.text_field.text_entity.color = color.light_gray
        self.highlight_color = color._32


class InspectorButton(Button):
    defaults = dict(model='quad', origin=(-.5,.5), text_origin=(-.5,0), text_color=color.light_gray, color=color.black90, highlight_color=color._32)

    def __init__(self, **kwargs):
        kwargs = __class__.defaults | kwargs
        super().__init__(**kwargs)
        self.text_entity.x = .025
        self.text_entity.scale *= .75


class ColorField(InspectorButton):
    def __init__(self, attr_name='color', is_shader_input=False, value=color.white, **kwargs):
        super().__init__(**kwargs)
        self.attr_name = attr_name
        self.is_shader_input = is_shader_input

        self.preview = Entity(parent=self, model=Quad(aspect=2/1), scale=(.5,.8), origin=(.5,.5), x=1, z=-.1, y=-.05, collider='box', on_click=self.on_click)
        # self.text_entity.scale *= .75
        self.value = value

    @property
    def value(self):
        return self.preview.color

    @value.setter
    def value(self, value):
        self.preview.color = value

    def on_click(self):
        LEVEL_EDITOR.color_menu.color_field = self
        LEVEL_EDITOR.color_menu.position = self.preview.get_position(relative_to=camera.ui).xy + Vec2(.025,-.01)
        LEVEL_EDITOR.menu_handler.state = 'color_menu'


class Inspector(Entity):
    def __init__(self):
        super().__init__(parent=LEVEL_EDITOR.ui, position=window.top_left+Vec2(.15,-.04))
        self.selected_entity = None
        self.ui = Entity(parent=self)
        self.name_field = InspectorInputField(parent=self.ui, default_value='name', origin=(-.5,.5), scale_x=.15*3, scale_y=.05*.75, color=hsv(210,.9,.6))
        self.input_fields = [self.name_field, ]
        self.transform_fields = []

        for y, names in enumerate((('x','y','z'), ('rotation_x','rotation_y','rotation_z'), ('scale_x','scale_y','scale_z'))):
            for x in range(3):
                default = '0'
                if y == 2:
                    default = '1'

                field = InspectorInputField(max_width=8, model='quad', parent=self.name_field, scale=(1/3,1), origin=(-.5,.5), default_value=default, limit_content_to=ContentTypes.math, x=x/3, y=-y-1, color=color._8)
                def on_submit(names=names, x=x, field=field):
                    try:
                        value = float(eval(field.text[:8]))
                        if isinstance(value, float):
                            field.text_field.text_entity.text = str(value)[:8]
                            for e in LEVEL_EDITOR.selection:
                                setattr(e, names[x], float(field.text_field.text_entity.text))
                    except: # invalid/incomplete math
                        # print('invalid')
                        return

                # field.submit_on = 'enter'
                field.on_submit = on_submit
                field.on_value_changed = on_submit

                self.transform_fields.append(field)
                # self.input_fields.append(field)

        for i in range(len(self.transform_fields)-1):
            self.transform_fields[i].next_field = self.transform_fields[i+1]

        self.fields = dict(
            model =   InspectorButton(parent=self.name_field, text='model: ', y=-4, on_click=Func(setattr, LEVEL_EDITOR.menu_handler, 'state', 'model_menu')),
            texture = InspectorButton(parent=self.name_field, text='texture: ', y=-4-1, on_click=Sequence(Func(setattr, LEVEL_EDITOR.menu_handler, 'state', 'texture_menu'), Func(setattr, LEVEL_EDITOR.texture_menu, 'target_attr', 'texture'))),
            color =   ColorField(parent=self.name_field, text='c:color: ', y=-4-2, attr_name='color', is_shader_input=False),
            collider_type = InspectorButton(parent=self.name_field, text='collider_type: ', y=-4-3, on_click=Func(setattr, LEVEL_EDITOR.menu_handler, 'state', 'collider_menu')),
            shader =  InspectorButton(parent=self.name_field, text='shader: ', y=-4-4, on_click=Func(setattr, LEVEL_EDITOR.menu_handler, 'state', 'shader_menu')),
        )


        Entity(model=Grid(3,3), parent=self.transform_fields[0], scale=3, origin=(-.5,.5), z=-.1, color=color._64)

        self.shader_inputs_parent = Entity(parent=self.name_field, y=-9)
        self.scale = .6
        self.update_inspector()


    def input(self, key):
        if key != 'left mouse up':
            return

        if LEVEL_EDITOR.selection and (mouse.left or held_keys['d']):
            if not self.selected_entity:
                self.update_inspector()
            elif self.selected_entity != LEVEL_EDITOR.selection[0]:
                self.update_inspector()


    def update_inspector(self):
        # print('update inspector')
        self.ui.enabled = bool(LEVEL_EDITOR.selection)
        if not LEVEL_EDITOR.selection:
            return

        self.selected_entity = LEVEL_EDITOR.selection[0]
        self.fields['color'].preview.color = LEVEL_EDITOR.selection[0].color
        self.name_field.text_field.text_entity.text = self.selected_entity.name

        for i, attr_name in enumerate(('x', 'y', 'z', 'rotation_x', 'rotation_y', 'rotation_z', 'scale_x', 'scale_y', 'scale_z')):
            self.transform_fields[i].text_field.text_entity.text = str(round(getattr(self.selected_entity, attr_name),4))

        for name in ('model', 'texture', 'collider_type', 'shader'):
            unique_field_values = tuple(set([getattr(e, name) for e in LEVEL_EDITOR.selection if hasattr(e, name)]))
            if unique_field_values == ():
                text = '*error*'

            elif len(unique_field_values) == 1: # all selected entities has the same value, so draw that
                text = unique_field_values[0]
                if hasattr(text, 'name'):
                    text = text.name
            else:
                text = '--- mixed ---'

            self.fields[name].text_entity.text = (f'{name[0]}:{text}')

        [destroy(e) for e in self.shader_inputs_parent.children]
        from ursina.prefabs.vec_field import VecField

        i = 0
        if self.selected_entity.shader:
            shader_inputs = {key: value for key, value in self.selected_entity.shader.default_input.items() if key != 'shadow_color'}
            for name, value in shader_inputs.items():
                instance_value = self.selected_entity.get_shader_input(name)
                if instance_value:
                    # print('use instance value,', instance_value)
                    value = instance_value

                if isinstance(value, str):  # texture
                    b = InspectorButton(parent=self.shader_inputs_parent, text=f' {name}: {value}', highlight_color=color.black90, y=-i)
                    b.text_entity.scale *= .6
                    b.on_click = Sequence(
                        Func(setattr, LEVEL_EDITOR.menu_handler, 'state', 'texture_menu'),
                        Func(setattr, LEVEL_EDITOR.texture_menu, 'target_attr', name)
                        )


                if isinstance(value, Vec2) or (hasattr(value, '__len__') and len(value) == 2):
                    field = VecField(default_value=instance_value, parent=self.shader_inputs_parent, model='quad', scale=(1,1), x=.5, y=-i-.5, text=f'  {name}')
                    for e in field.fields:
                        e.text_field.scale *= .6
                        e.text_field.text_entity.color = color.light_gray
                    field.text_entity.scale *= .6*.75
                    field.text_entity.color = color.light_gray

                    def on_submit(name=name, field=field):
                        for e in LEVEL_EDITOR.selection:
                            # setattr(e, name, float(field.text_field.text_entity.text))
                            e.set_shader_input(name, field.value)
                    field.on_value_changed = on_submit

                # # float
                # # int
                # # Vec3

                elif isinstance(value, Color):
                    color_field = ColorField(parent=self.shader_inputs_parent, text=f' {name}', y=-i, is_shader_input=True, attr_name=name, value=value)
                    color_field.text_entity.scale *= .6


                i += 1

        i += 0
        if hasattr(self.selected_entity, 'draw_inspector'):
            divider = Entity(parent=self.shader_inputs_parent, model='quad', collider='box', origin=(-.5,.5), scale=(1,.5), color=color.black90, y=-i)
            i += 1
            # print('-------------', self.selected_entity.draw_inspector())
            for name, _type in self.selected_entity.draw_inspector().items():
                if not hasattr(self.selected_entity, name):
                    continue
                attr = getattr(self.selected_entity, name)
                if attr is False or attr is True:
                # if isinstance(attr, bool):
                    b = InspectorButton(parent=self.shader_inputs_parent, text=f' {name}:', highlight_color=color.red, y=-i, origin=(-.5,0))
                    b.text_entity.scale *= .6
                    def toggle_value(name=name):
                        new_value = not getattr(self.selected_entity, name)
                        for e in LEVEL_EDITOR.selection:
                            setattr(e, name, new_value)
                            if hasattr(e, 'generate'):
                                e.generate()

                    b.on_click = toggle_value

                elif _type in (float, int):
                    field = VecField(default_value=attr, parent=self.shader_inputs_parent, model='quad', scale=(1,1), x=.5, y=-i, text=f'  {name}')
                    for e in field.fields:
                        e.text_field.scale *= .6
                        e.text_field.text_entity.color = color.light_gray
                    field.text_entity.scale *= .6*.75
                    field.text_entity.color = color.light_gray

                    def on_submit(name=name, field=field):
                        for e in LEVEL_EDITOR.selection:
                            setattr(e, name, field.value)

                    field.on_value_changed = on_submit

                elif isinstance(_type, type):
                    text = attr
                    if hasattr(attr, 'name'):
                        text = attr.__name__

                    b = InspectorButton(parent=self.shader_inputs_parent, text=f' {name}: {text}', y=-i, origin=(-.5,0))
                    b.text_entity.scale *= .6
                    b.on_click = Func(setattr, LEVEL_EDITOR.menu_handler, 'state', 'class_menu')

                i += 1



class MenuHandler(Entity):
    def __init__(self):
        super().__init__(parent=LEVEL_EDITOR)
        self._state = None
        self.states = {
            'None' : Entity(),
            'model_menu' : LEVEL_EDITOR.model_menu,
            'texture_menu' : LEVEL_EDITOR.texture_menu,
            'shader_menu' : LEVEL_EDITOR.shader_menu,
            'color_menu' : LEVEL_EDITOR.color_menu,
            'collider_menu': LEVEL_EDITOR.collider_menu,
            'class_menu': LEVEL_EDITOR.class_menu
        }
        self.keybinds = {'m' : 'model_menu', 'v' : 'texture_menu', 'n' : 'shader_menu', 'b' : 'color_menu', 'escape' : 'None'}

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        target_state = self.states[value]
        print('toggle:', value, 'from:', self._state)
        if self._state == value:
            target_state.enabled = not target_state.enabled
            return

        for key, e in self.states.items():        # only show set state and disable the rest
            if e:
                e.enabled = value == key

        self._state = value


    def input(self, key):
        if key == 'escape' and self.state != 'None':
            self.state = 'None'
            return
        # print(key, self.keybinds)
        if self.state != 'None':
            return

        if not held_keys['control'] and not held_keys['shift'] and not held_keys['alt'] and key in self.keybinds and LEVEL_EDITOR.selection:
            self.state = self.keybinds[key]
            # print('sets state:', self.keybinds[key], self.state)

class AssetMenu(Entity):
    def __init__(self):
        super().__init__(parent=LEVEL_EDITOR.ui, enabled=False, z=-2, name=__class__.__name__)
        self.button_list = ButtonList({}, parent=self, font='VeraMono.ttf', x=-.25*.75, scale=.75)
        self.bg = Entity(parent=self.button_list, model='quad', collider='box', color=color.black33, on_click=self.disable, z=.1, scale=100)

    def on_enable(self):
        if not self.asset_names:
            print('no texture assets found')
            # return
        asset_dict = {name : Func(self.on_select_asset, name) for name in self.asset_names}
        self.button_list.button_dict = asset_dict
        self.button_list.y = len(asset_dict) / 2 * self.button_list.button_height * Text.size
        self.button_list.x = mouse.x
        self.button_list.y = mouse.y


class ModelMenu(AssetMenu):
    def on_enable(self):
        # self.model_names = [e.stem for e in application.internal_models_compressed_folder.glob('**/*.ursinamesh')]
        self.asset_names = ['None', 'cube', 'sphere', 'plane']
        for file_type in ('.bam', '.obj', '.ursinamesh'):
            self.asset_names += [e.stem for e in application.asset_folder.glob(f'**/*{file_type}') if not 'animation' in e.stem]

        super().on_enable()

    def on_select_asset(self, name):
        if name == 'None':
            name = None

        changes = []
        for e in LEVEL_EDITOR.selection:
            index = LEVEL_EDITOR.entities.index(e)
            if not e.model:
                changes.append((index, 'model', None, name))
            else:
                changes.append((index, 'model', e.model.name, name))

        for e in LEVEL_EDITOR.selection:
            e.model = name
            if name == 'cube':
                e.collider = 'cube'
            else:
                e.collider = None

        LEVEL_EDITOR.menu_handler.state = 'None'


class TextureMenu(AssetMenu):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_attr = 'texture'

    def on_enable(self):
        search_for = ''

        self.asset_names = ['None', 'white_cube', 'brick', 'grass_tintable', 'radial_gradient', 'cog']
        for file_type in ('.png', '.jpg', '.jpeg'):
            self.asset_names += [e.stem for e in application.asset_folder.glob(f'**/{search_for}*{file_type}')]

        super().on_enable()

    def on_select_asset(self, name):
        if name == 'None':
            name = None

        if self.target_attr == 'texture':
            LEVEL_EDITOR.current_scene.undo.record_undo([(LEVEL_EDITOR.entities.index(e), 'texture', e.texture, name) for e in LEVEL_EDITOR.selection])
            for e in LEVEL_EDITOR.selection:
                e.texture = name
        else:
            LEVEL_EDITOR.current_scene.undo.record_undo([(LEVEL_EDITOR.entities.index(e), self.target_attr, e.get_shader_input(self.target_attr), name) for e in LEVEL_EDITOR.selection])
            for e in LEVEL_EDITOR.selection:
                e.set_shader_input(self.target_attr, name)

        LEVEL_EDITOR.inspector.update_inspector()
        LEVEL_EDITOR.menu_handler.state = 'None'


class ShaderMenu(AssetMenu):
    def on_enable(self):
        self.asset_names = [
            'unlit_shader',
            'lit_with_shadows_shader',
            'triplanar_shader',
            'matcap_shader',
            'normals_shader',
        ]
        super().on_enable()

    def on_select_asset(self, name):
        LEVEL_EDITOR.menu_handler.state = 'None'
        LEVEL_EDITOR.current_scene.undo.record_undo([(LEVEL_EDITOR.entities.index(e), 'shader', e.shader, name) for e in LEVEL_EDITOR.selection])
        for e in LEVEL_EDITOR.selection:
            exec(f'from ursina.shaders import {name}')
            exec(f'e.shader = {name}')
        LEVEL_EDITOR.inspector.update_inspector()


class ColorMenu(Entity):
    def __init__(self):
        super().__init__(parent=LEVEL_EDITOR.ui, enabled=False)
        self.bg = Entity(parent=self, collider='box', z=.1, color=color.black, alpha=.8, origin=(-.5,.5), scale=(.6,.15), position=(-.05,.03), model=Quad(aspect=.6/.15))

        self.h_slider = Slider(name='h', min=0, max=360, step=1, text='h', dynamic=True, world_parent=self, on_value_changed=self.on_slider_changed)
        self.h_slider.bg.color = color.white
        self.h_slider.bg.texture = 'rainbow'
        self.h_slider.bg.texture.filtering = True

        self.s_slider = Slider(name='s', min=0, max=100, step=1, default=50, text='s', dynamic=True, world_parent=self, on_value_changed=self.on_slider_changed)
        self.s_slider.bg.color = color.white
        self.s_slider.bg.model.colors = [color.white for i in self.s_slider.bg.model.vertices]

        self.v_slider = Slider(name='v', min=0, max=100, default=50, step=1, text='v', dynamic=True, world_parent=self, on_value_changed=self.on_slider_changed)
        self.v_slider.bg.model.colors = [color.black for i in self.v_slider.bg.model.vertices]
        self.v_slider.bg.color = color.white

        self.a_slider = Slider(name='a', min=0, max=100, default=100, step=1, text='a', dynamic=True, world_parent=self, on_value_changed=self.on_slider_changed)
        self.a_slider.bg.model.colors = [color.white for i in self.a_slider.bg.model.vertices]
        self.a_slider.bg.color = color.white
        for i, v in enumerate(self.a_slider.bg.model.vertices):
            if v[0] < 0:
                self.a_slider.bg.model.colors[i] = color.clear
        self.a_slider.bg.model.generate()

        for i, e in enumerate((self.h_slider, self.s_slider, self.v_slider, self.a_slider)):
            e.y = -i * .03
            e.knob.color = color.white

        self.scale *= .5

        self.bg = Entity(parent=self, model='quad', collider='box', visible_self=False, scale=10, z=1, on_click=self.close)
        self.apply_color = True     # set to False when you want to move the sliders but not update the color of the entities.


    def on_slider_changed(self):
        value = color.hsv(self.h_slider.value, self.s_slider.value/100, self.v_slider.value/100, self.a_slider.value/100)

        if self.apply_color:
            LEVEL_EDITOR.inspector.fields['color'].preview.color = value
            if not LEVEL_EDITOR.inspector.fields['color'].is_shader_input:
                for e in LEVEL_EDITOR.selection:
                    e.color = value
            else:
                # print('is shader input, set', inspector.fields['color'].attr_name)
                for e in LEVEL_EDITOR.selection:
                    e.set_shader_input(LEVEL_EDITOR.inspector.fields['color'].attr_name, value)


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


    def on_enable(self):
        for e in LEVEL_EDITOR.selection:
            e.original_color = e.color

        self.apply_color = False
        self.h_slider.value = LEVEL_EDITOR.inspector.fields['color'].preview.color.h
        self.s_slider.value = LEVEL_EDITOR.inspector.fields['color'].preview.color.s * 100
        self.v_slider.value = LEVEL_EDITOR.inspector.fields['color'].preview.color.v * 100
        self.a_slider.value = LEVEL_EDITOR.inspector.fields['color'].preview.color.a * 100
        self.apply_color = True


    def close(self):
        LEVEL_EDITOR.menu_handler.state = 'None'
        LEVEL_EDITOR.current_scene.undo.record_undo([(LEVEL_EDITOR.entities.index(e), 'color', e.original_color, e.color) for e in LEVEL_EDITOR.selection])


class ColliderMenu(AssetMenu):
    def on_enable(self):
        self.asset_names = ['None', 'box', 'sphere', 'mesh', ]
        super().on_enable()

    def on_select_asset(self, name):
        if name == 'None':
            name = None
        # LEVEL_EDITOR.current_scene.undo.record_undo([(LEVEL_EDITOR.entities.index(e), 'collider', e.texture, name) for e in LEVEL_EDITOR.selection])
        for e in LEVEL_EDITOR.selection:
            e.collider_type = name

        LEVEL_EDITOR.inspector.update_inspector()
        LEVEL_EDITOR.menu_handler.state = 'None'


class ClassMenu(AssetMenu):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.available_classes = {'None': None}

    def on_enable(self):
        self.asset_names = self.available_classes.keys()
        super().on_enable()

    def on_select_asset(self, name):
        # LEVEL_EDITOR.current_scene.undo.record_undo([(LEVEL_EDITOR.entities.index(e), 'collider', e.texture, name) for e in LEVEL_EDITOR.selection])
        for e in LEVEL_EDITOR.selection:
            if hasattr(e, 'class_to_spawn'):
                e.class_to_spawn = name

        LEVEL_EDITOR.inspector.update_inspector()
        LEVEL_EDITOR.menu_handler.state = 'None'


class Help(Button):
    def __init__(self, **kwargs):
        super().__init__(parent=LEVEL_EDITOR.ui, text='?', scale=.025, model='circle', origin=(-.5,.5), text_origin=(0,0), position=window.top_left)
        self.tooltip = Text(
            position=self.position + Vec3(.05,-.05,-10),
            # wordwrap=0,
            font='VeraMono.ttf',
            enabled=False,
            text=dedent('''
                Hotkeys:
                n:          add new cube

                d:          quick drag
                w:          move tool
                x/y/z:      hold to quick move on axis

                c:          quick rotate on y axis
                t:          tilt

                e:          scale tool
                s:          quick scale
                s + x/y/z:  quick scale on axis

                f:          move editor camera to point
                shift+f:    reset editor camera position
                shift+p:    toggle perspective/orthographic
                shift+d:    duplicate
            ''').strip(),
            background=True,
            scale=.5
        )
        self.tooltip.background.color = color.black
        self.tooltip.original_scale = .75


class Duplicator(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=LEVEL_EDITOR, clones=None)
        self.plane = Entity(model='plane', collider='box', scale=Vec3(100,.1,100), enabled=False, visible=False)
        self.dragger = Draggable(parent=scene, model=None, collider=None, enabled=False)
        self.dragging = False
        self.start_position = None
        self.clone_from_position = None
        self.axis_lock = None
        self.axis_lock_gizmos = [
            Entity(model='cube', scale=Vec3(100,.01,.01), color=color.magenta, parent=self.dragger, unlit=True, enabled=False),
            Entity(model='cube', scale=Vec3(.01,100,.01), color=color.yellow, parent=self.dragger, unlit=True, enabled=False),
            Entity(model='cube', scale=Vec3(.01,.01,100), color=color.cyan, parent=self.dragger, unlit=True, enabled=False),
        ]

    def update(self):
        if self.plane.enabled:
            self.dragger.position = mouse.world_point
            if self.axis_lock is not None:

                self.axis_lock_gizmos[self.axis_lock].enabled = True
                if self.axis_lock == 0:
                    self.dragger.z = self.start_position.z
                if self.axis_lock == 2:
                    self.dragger.x = self.start_position.x


    def input(self, key):
        combined_key = input_handler.get_combined_key(key)
        if combined_key == 'shift+d' and LEVEL_EDITOR.selection:
            # print('duplicate')

            LEVEL_EDITOR.menu_handler.state = 'None'
            self.clones = []
            for e in LEVEL_EDITOR.selection:
                clone = deepcopy(e)
                clone.original_parent = e.parent
                clone.color = e.color
                clone.shader = e.shader
                clone.origin = e.origin
                clone.selectable = True
                for key, value in e._shader_inputs.items():
                    clone.set_shader_input(key, value)

                clone.collision = False
                clone.collider_type = e.collider_type
                self.clones.append(clone)

            LEVEL_EDITOR.entities.extend(self.clones)
            LEVEL_EDITOR.selection = self.clones
            LEVEL_EDITOR.current_scene.undo.record_undo(('delete entities', [LEVEL_EDITOR.entities.index(en) for en in self.clones], [repr(e) for e in self.clones],))

            self.clone_from_position = self.clones[-1].position
            self.plane.y = LEVEL_EDITOR.selection[-1].world_y
            self.plane.enabled = True

            mouse.traverse_target = self.plane
            mouse.update()
            self.start_position = mouse.world_point
            self.dragger.world_position = self.start_position
            self.dragger.enabled = True
            self.axis_lock = None

            for e in LEVEL_EDITOR.selection:
                e.world_parent = self.dragger


        elif self.plane.enabled and key == 'left mouse up':
            for e in self.clones:
                e.world_parent = e.original_parent

            self.plane.enabled = False
            self.dragger.enabled = False
            self.clones = []
            mouse.traverse_target = scene
            [e.disable() for e in self.axis_lock_gizmos]
            LEVEL_EDITOR.render_selection()

        elif self.plane.enabled and key == 'middle mouse down':
            if self.axis_lock == None:
                delta_position = (abs(self.dragger.x-self.start_position.x), abs(self.dragger.y-self.start_position.y), abs(self.dragger.z-self.start_position.z))
                max_val = max(delta_position)
                self.axis_lock = delta_position.index(max_val)
                for e in self.axis_lock_gizmos:
                    e.world_position = self.clones[-1].world_position
                # print('lock on axis:', delta_position, max_val, self.axis_lock)
            else:
                self.axis_lock = None



class SunHandler(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=LEVEL_EDITOR, **kwargs)
        self.sun = DirectionalLight(shadow_map_resolution=(2048,2048))
        self.sun.look_at(Vec3(-2,-1,-1))
        # self.update_bounds()

    def update_bounds(self, entity):
        self.sun.update_bounds(entity)

    def input(self, key):
        if key == 'l':
            print('toggle sun')
            self.update_bounds()


from ursina.prefabs.radial_menu import RadialMenu
class RightClickMenu(Entity):
    def __init__(self):
        super().__init__(parent=LEVEL_EDITOR.ui)
        self.radial_menu = RadialMenu(
            parent=LEVEL_EDITOR.ui,
            buttons = (
                Button(highlight_color=color.azure, model='circle', text='Model', scale=1.5, on_click=Func(setattr, LEVEL_EDITOR.menu_handler, 'state', 'model_menu')),
                Button(highlight_color=color.azure, model='circle', text='Tex', scale=1.5, on_click=Sequence(Func(setattr, LEVEL_EDITOR.menu_handler, 'state', 'texture_menu'), Func(setattr, LEVEL_EDITOR.texture_menu, 'target_attr', 'texture'))),
                Button(highlight_color=color.azure, model='circle', text='Col', scale=1.5, on_click=Sequence(Func(setattr, LEVEL_EDITOR.menu_handler, 'state', 'color_menu'), Func(setattr, LEVEL_EDITOR.color_menu, 'position', mouse.position))),
                Button(highlight_color=color.azure, model='circle', text='Sh',  scale=1.5, on_click=Func(setattr, LEVEL_EDITOR.menu_handler, 'state', 'shader_menu')),
                Button(highlight_color=color.black, model='circle', text='del', scale=.75, color=color.red, on_click=LEVEL_EDITOR.deleter.delete_selected),
                Button(highlight_color=color.azure, model='circle', text='Coll', scale=1.5),
            ),
            enabled=False,
            scale=.05
        )

    def input(self, key):
        if key == 'right mouse down':
            self.start_click_pos = mouse.position

        if key == 'right mouse up':
            if LEVEL_EDITOR.selection and sum(abs(e) for e in mouse.position-self.start_click_pos) < .005 and LEVEL_EDITOR.selector.get_hovered_entity() in LEVEL_EDITOR.selection:
                self.radial_menu.enabled = True



class Search(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=LEVEL_EDITOR.ui, **kwargs)
        self.input_field = InputField(parent=LEVEL_EDITOR.ui, enabled=False)

    def input(self, key):
        if key == 'space' and LEVEL_EDITOR.selection:
            self.input_field.enabled = True
            self.input_field.text = ''

        # elif len(key) == 1:
        #     print('---', self.input_field.text)

def get_major_axis_relative_to_view(entity): # if we're looking at the entity from the right/left, return 0, top/bot:1, front/back: 2
    r = round(camera.back.dot(entity.right), 1)
    u = round(camera.back.dot(entity.up), 1)
    f = round(camera.back.dot(entity.forward), 1)
    dir = (r, u, f)
    axis_index = dir.index(max(dir, key=abs))
    is_positive_direction = dir[axis_index] > 0

    return axis_index, is_positive_direction


if __name__ == '__main__':
    from ursina import *
    # from ursina.editor.level_editor import LevelEditor

    app = Ursina(vsync=False)

    class Tree(Entity):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.model = 'cube'
            self.color = color.brown

            self.top = Entity(name='tree_top', parent=self, y=1.5, model='cube', color=color.green, selectable=True)
            LEVEL_EDITOR.entities.append(self.top)


    level_editor = LevelEditor()
    # level_editor.goto_scene(0,0)



    level_editor.class_menu.available_classes |= {'WhiteCube': WhiteCube, 'EditorCamera':EditorCamera, }

    app.run()


    # level_editor.prefabs.append(Tree)
    # level_editor.spawner.update_menu()

    # level_editor.selection = [level_editor.entities[0], ]
    # window.center_on_screen()
    # Sky()
