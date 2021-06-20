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
        scene_file_content = dedent(f'''
            class Scene(Entity):
                def __init__(self, **kwargs):
                    super().__init__(**kwargs)
        ''')
        temp_entity= Entity()
        attrs_to_save = ('position', 'rotation', 'scale', 'model', 'origin', 'color',
            # 'texture'
            )

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

            scene_file_content += ', ignore=True)\n' # TODO: add if it has a custom name

        # print('scene_file_content:\n', scene_file_content)
        self.path = level_editor.scene_folder/(self.name+'.py')
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(scene_file_content)
        print('saved:', self.path)


    def load(self):
        if not self.path:
            print('cant load scene, no path')
            return
        if self.scene_parent:
            print('error, scene already loaded')
            return

        t = perf_counter()
        with open(self.path) as f:
            try:
                exec(f.read())
                self.scene_parent = eval(f'Scene()')
                self.scene_parent.name = self.name
                self.entities = [e for e in scene.entities if e.has_ancestor(self.scene_parent)]
                for e in self.entities:
                    # e.collider = 'box'
                    # e.collision = False
                    e.shader = lit_with_shadows_shader
                    e.ignore = True
            except Exception as e:
                print('error in scene:', self.name, e)

        if self.scene_parent:
            print(f'loaded scene: "{self.name}" in {perf_counter()-t}')
            return self.scene_parent


    def unload(self):
        [destroy(e) for e in self.entities]
        # if not self.scene_parent:
        #     # print('cant unload scene, its already empty')
        #     return

        self.selection = []
        self.entities = []
        destroy(self.scene_parent)


class LevelEditor(Entity):
    def __init__(self, **kwargs):
        super().__init__(eternal=True)
        self.scene_folder = application.asset_folder / 'scenes'
        self.scenes = [[Scene(x, y, f'untitled_scene[{x},{y}]') for y in range(8)] for x in range(8)]
        # self.current_scene = self.scenes[0][0]
        # self.current_scene.load()
        # print('scene_folder:', self.scene_folder)

        self.grid = Entity(parent=self, model=Grid(16,16), rotation_x=90, scale=32, collider='box', color=color.white33, collision=False)
        self.origin_mode = 'center'
        self.origin_mode_menu = ButtonGroup(['last', 'center', 'individual'], min_selection=1, position=window.top)
        self.editor_camera = EditorCamera(parent=self, rotation_x=20)
        self.ui = Entity(parent=camera.ui)
        self.on_enable = Func(self.ui.enable)
        self.on_disable = Func(self.ui.disable)


    @property
    def entities(self):
        return self.current_scene.entities

    @property
    def selection(self):
        return self.current_scene.selection

    @selection.setter
    def selection(self, value):
        self.current_scene.selection = value


    def input(self, key):
        if held_keys['control'] and not held_keys['shift'] and not held_keys['alt'] and key == 's':
            if not self.current_scene:
                print('no current_scene, cant save')
                return

            self.current_scene.save()


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
        for data in self.undo_data[self.undo_index]:
            target, attr, original, new = data
            setattr(target, attr, original)

        selector.render_selection() # make sure the gizmo position updates
        self.undo_index -= 1

    def redo(self):
        if self.undo_index+2 > len(self.undo_data):
            return
        for data in self.undo_data[self.undo_index+1]:
            target, attr, original, new = data
            setattr(target, attr, new)

        selector.render_selection() # make sure the gizmo position updates
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

if not load_model('arrow'):
    p = Entity(enabled=False)
    Entity(parent=p, model='cube', scale=(1,.05,.05))
    Entity(parent=p, model=Cone(4, direction=(1,0,0)), x=.5, scale=.2)
    arrow_model = p.combine()
    arrow_model.save('arrow.ursinamesh')

if not load_model('scale_gizmo'):
    p = Entity(enabled=False)
    Entity(parent=p, model='cube', scale=(.05,.05,1))
    Entity(parent=p, model='cube', z=.5, scale=.2)
    arrow_model = p.combine()
    arrow_model.save('scale_gizmo.ursinamesh')


class GizmoArrow(Draggable):
    def __init__(self, model='arrow', collider='box', **kwargs):
        super().__init__(model=model, origin_x=-.55, always_on_top=True, render_queue=1, is_gizmo=True, shader=unlit_shader, **kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def drag(self):
        self.world_parent = level_editor
        self.gizmo.world_parent = self
        for e in level_editor.selection:
            e.world_parent = self
            e.always_on_top = False
            e._original_world_position = e.world_position

    def drop(self):
        self.gizmo.world_parent = level_editor
        changes = []
        for e in level_editor.selection:
            e.world_parent = level_editor
            changes.append([e, 'world_position', e._original_world_position, e.position])

        self.parent = self.gizmo.arrow_parent
        self.position = (0,0,0)
        level_editor.current_scene.undo.record_undo(changes)
        selector.render_selection()



class Gizmo(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=level_editor, enabled=False)
        self.arrow_parent = Entity(parent=self)
        self.arrows = {
            'xz' : GizmoArrow(parent=self.arrow_parent, gizmo=self, model='cube', scale=.6, scale_y=.05, origin=(-.75,0,-.75), color=lerp(color.magenta, color.cyan, .5), plane_direction=(0,1,0)),
            'x'  : GizmoArrow(parent=self.arrow_parent, gizmo=self, color=axis_colors['x'], lock=(0,1,1)),
            'y'  : GizmoArrow(parent=self.arrow_parent, gizmo=self, rotation=(0,0,-90), color=axis_colors['y'], lock=(1,0,1)),
            'z'  : GizmoArrow(parent=self.arrow_parent, gizmo=self, rotation=(0,-90,0), color=axis_colors['z'], plane_direction=(0,1,0), lock=(1,1,0)),
        }
        for e in self.arrow_parent.children:
            e.highlight_color = color.white



class ScaleGizmo(Draggable):
    def __init__(self, **kwargs):
        super().__init__(parent=gizmo, model='cube', scale=.25, color=color.orange, visible=True, always_on_top=True, render_queue=1, is_gizmo=True, dragging=False, shader=unlit_shader)
        self.scaler = Entity(parent=gizmo)
        self.axis = Vec3(1,1,1)
        self.on_click = Func(setattr, self, 'axis', Vec3(1,1,1))
        self.arrows = {}

        for i, dir in enumerate((Vec3(1,0,0), Vec3(0,1,0), Vec3(0,0,1))):
            b = Button(parent=self, model='scale_gizmo', origin_z=-.5, scale=4, collider='box',
                color=axis_colors[('x','y','z')[i]], is_gizmo=True, always_on_top=True, render_queue=1, shader=unlit_shader,
                on_click=Sequence(Func(setattr, self, 'axis', dir), Func(self.drag)))
            b.look_at(dir)
            self.arrows['xyz'[i]] = b


    def drag(self):
            for e in level_editor.selection:
                e.world_parent = self.scaler
                e._original_world_scale = e.world_scale
            self.dragging = True

    def drop(self):
        changes = []
        for e in level_editor.selection:
            e.world_parent = level_editor
            changes.append([e, 'world_scale', e._original_world_scale, e.world_scale])

        level_editor.current_scene.undo.record_undo(changes)
        self.dragging = False
        self.scaler.scale = 1
        selector.render_selection()



    def update(self):
        if self.dragging:
            if not level_editor.origin_mode_menu.value[0] == 'individual':
                self.scaler.scale += Vec3(sum(mouse.velocity), sum(mouse.velocity), sum(mouse.velocity)) * 100 * time.dt * self.axis
            else:
                for e in level_editor.selection:
                    e.scale += Vec3(sum(mouse.velocity), sum(mouse.velocity), sum(mouse.velocity)) * 100 * time.dt * self.axis


class GizmoToggler(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.animator = Animator({
            'w' : gizmo.arrow_parent,
            'e' : scale_gizmo,
            # 'r' :
        })

    def input(self, key):
        if key in self.animator.animations:
            self.animator.state = key


class QuickGrabber(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=level_editor,
            gizmos_to_toggle={
                'g' : gizmo.arrows['xz'],
                'x' : gizmo.arrows['x'],
                'y' : gizmo.arrows['y'],
                'z' : gizmo.arrows['z'],
                's' : scale_gizmo,
                'sx' : scale_gizmo,
                'sy' : scale_gizmo,
                'sz' : scale_gizmo,

            },
            clear_selection = False
            )

    def input(self, key):
        if held_keys['control'] or held_keys['shift'] or held_keys['alt']:
            return

        if held_keys['s'] and not key == 's':
            key = 's' + key

        if key in ('g', 'x', 'y', 'z'):
            self.original_gizmo_state = gizmo_toggler.animator.state
            gizmo_toggler.animator.state = 'w'

        elif key in ('s', 'sx', 'sy', 'sz'):
            self.original_gizmo_state = gizmo_toggler.animator.state
            gizmo_toggler.animator.state = 'e'

            if not key == 's':
                scale_gizmo.axis = (Vec3(1,0,0), Vec3(0,1,0), Vec3(0,0,1))[('sx', 'sy', 'sz').index(key)]

        # elif key == 'r':
        #     gizmo_toggler.state = 'r'

        if key in self.gizmos_to_toggle.keys():
            gizmo.arrow_parent.visible = False
            scale_gizmo.visible = False
            self.gizmos_to_toggle[key].visible_self = False
            if not key in ('sx', 'sy', 'sz'):
                self.clear_selection = not level_editor.selection

            if not level_editor.selection:
                selector.input('left mouse down')
            elif gizmo_toggler.animator.state == 'w':
                mouse.position = self.gizmos_to_toggle[key].screen_position

            self.gizmos_to_toggle[key].input('left mouse down')
            invoke(self.gizmos_to_toggle[key].start_dragging, delay=1/60)

        if key.endswith(' up') and key[:-3] in self.gizmos_to_toggle.keys():
            key = key[:-3]
            self.gizmos_to_toggle[key].input('left mouse up')
            if self.clear_selection:
                level_editor.selection.clear()
                selector.render_selection()

            gizmo.arrow_parent.visible = True
            scale_gizmo.visible = True
            scale_gizmo.axis = Vec3(1,1,1)
            self.gizmos_to_toggle[key].visible_self = True
            gizmo_toggler.animator.state = self.original_gizmo_state

class Selector(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.point_renderer = Entity(parent=self, model=Mesh([], mode='point', thickness=20, render_points_in_3d=0),
            texture='circle', always_on_top=True, unlit=True, render_queue=1,
            # states=LoopingList(['2d','3d',None])
            )


        for key, value in kwargs.items():
            setattr(self, key, value)


    def input(self, key):
        if key == 'left mouse down':
            if hasattr(mouse.hovered_entity, 'is_gizmo'):
                return

            entities_in_range = [(distance(e.screen_position, mouse.position), e) for e in level_editor.entities]
            entities_in_range = [e for e in entities_in_range if e[0] < .03]
            entities_in_range.sort()

            clicked_entity = None
            if entities_in_range:
                clicked_entity = entities_in_range[0][1]

            if clicked_entity in level_editor.entities and not clicked_entity in level_editor.selection and not held_keys['alt']:
                if held_keys['shift']:
                    level_editor.selection.append(clicked_entity) # append
                else:
                    level_editor.selection = [clicked_entity, ]   # overwrite

            if held_keys['alt'] and clicked_entity in level_editor.selection:
                level_editor.selection.remove(clicked_entity) # remove

            if not clicked_entity and not held_keys['shift'] and not held_keys['alt']: # clear
                level_editor.selection.clear()

            self.render_selection()

            # clicked_entity = mouse.hovered_entity
        #     for e in level_editor.entities:
        #         e.collision = True
        #
        #     if hasattr(mouse.hovered_entity, 'is_gizmo'):
        #         return
        #         print('clicked on gizmo')
        #
        #     # wait one frame to get hovered entity so the colliders are turned on
        #     invoke(self.select_hovered_entity, delay=1/60)
        #
        # elif key == 'left mouse up':
        #     for e in level_editor.entities:
        #         e.collision = False

        if held_keys['control'] and key == 'a':
            level_editor.selection = [e for e in level_editor.entities]
            self.render_selection()

        elif key == 'h':
            self.point_renderer.enabled = not self.point_renderer.enabled


    def select_hovered_entity(self):
        clicked_entity = mouse.hovered_entity
        if clicked_entity in level_editor.entities and not clicked_entity in level_editor.selection and not held_keys['alt']:
            if held_keys['shift']:
                level_editor.selection.append(clicked_entity) # append
            else:
                level_editor.selection = [clicked_entity, ]   # overwrite

        if held_keys['alt'] and clicked_entity in level_editor.selection:
            level_editor.selection.remove(clicked_entity) # remove

        if not clicked_entity and not held_keys['shift'] and not held_keys['alt']: # clear
            level_editor.selection.clear()

        self.render_selection()


    def render_selection(self):
        self.point_renderer.model.vertices = [e.world_position for e in level_editor.entities]
        self.point_renderer.model.colors = [color.azure if e in level_editor.selection else color.white66 for e in level_editor.entities]
        self.point_renderer.model.generate()

        gizmo.enabled = bool(level_editor.selection)

        if level_editor.selection:
            if level_editor.origin_mode_menu.value[0] in ('last', 'individual'):
                gizmo.position = level_editor.selection[-1].position
            else: # center
                gizmo.position = sum([e.position for e in level_editor.selection]) / len(level_editor.selection)



class SelectionBox(Entity):
    def input(self, key):
        if key == 'left mouse down':
            if mouse.hovered_entity and not mouse.hovered_entity in level_editor.selection:
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

                pos = e.screen_position
                if pos.x > self.x and pos.x < self.x + abs(self.scale_x) and pos.y > self.y and pos.y < self.y + abs(self.scale_y):
                    if self.mode in ('add', 'new') and not e in level_editor.selection:
                        level_editor.selection.append(e)
                    elif self.mode == 'subtract' and e in level_editor.selection:
                        level_editor.selection.remove(e)

            selector.render_selection()
            self.mode = 'new'

    def update(self):
        if mouse.left:
            if mouse.x == mouse.start_x and mouse.y == mouse.start_y:
                return

            self.scale_x = mouse.x - self.x
            self.scale_y = mouse.y - self.y


class Spawner(Entity):
    def input(self, key):
        if key == 'n':
            if not mouse.hovered_entity in level_editor.entities:
                level_editor.grid.collision = True
            self.target = Entity(
                model='cube',
                origin_y=-.5,
                collider='box',
                shader=lit_with_shadows_shader,
                texture='white_cube',
                # color=color.white,
                position=mouse.world_point,
                collision=False,
                )
            level_editor.current_scene.entities.append(self.target)

        elif key == 'n up':
            # self.target.collision = True
            self.target = None
            level_editor.grid.collision = False

    def update(self):
        if held_keys['n'] and mouse.world_point and self.target:
            self.target.position = mouse.world_point


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
        self.content_renderer = Entity(parent=self.menu, scale=1/8, position=(-1,-.5,-1), model=Mesh(), color='#333333') # scales the content so I can set the position as (x,y) instead of (-1+(x/8),-.5+(y/8))
        self.cursor = Entity(parent=self.content_renderer, model='quad', color=color.lime, origin=(-.5,-.5), z=-2, alpha=.5)
        self.current_scene_idicator = Entity(parent=self.content_renderer, model='circle', color=color.azure, origin=(-.5,-.5), z=-1)
        # self.tabs = [Button(parent=self.menu, scale=(1/4,1/8), position=(-1+(i/4),.5), origin=(-.5,-.5), color=color.hsv(90*i,.5,.3)) for i in range(4)]


        self.current_scene_label = Text(parent=self.menu, x=-1, y=-.5, text='current scene:', z=-10, scale=4)

        self.load_scenes()
        level_editor.current_scene = level_editor.scenes[0][0]
        self.goto_scene(0, 0)
        self.draw()


    def load_scenes(self):
        for scene_file in level_editor.scene_folder.glob('*.py'):
            if '__' in scene_file.name:
                continue

            print('found scene:', scene_file)
            name = scene_file.stem
            if '[' in name and ']' in name:
                x, y = [int(e) for e in name.split('[')[1].split(']')[0].split(',')]
                print('scene is at coordinate:', x, y)
                level_editor.scenes[x][y].path = scene_file



    def draw(self):
        self.content_renderer.model.clear()
        for x in range(8):
            for y in range(8):
                if level_editor.scenes[x][y].path:
                    self.content_renderer.model.vertices += [Vec3(*v)+Vec3(x+.5,y+.5,0) for v in load_model('quad').vertices]

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

        if key == 'left mouse up' and self.menu.hovered:
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

            elif held_keys['alt'] and not held_keys['shift']: # remove
                level_editor.scenes[x][y].unload()


        # hotkeys for loading neightbour levels
        if held_keys['shift'] and held_keys['alt'] and key in 'wasd':
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
        self.current_scene_idicator.position = (x,y)
        [[level_editor.scenes[_x][_y].unload() for _x in range(8)] for _y in range(8)]
        level_editor.current_scene = level_editor.scenes[x][y]
        level_editor.current_scene.load()
        self.current_scene_label.text = level_editor.current_scene.name
        self.draw()
        selector.render_selection()


# class AssetBrowser(Entity()):
#     def __init__(self, **kwargs):
#         super().__init__(parent=level_editor.ui)
#         self.asset_scene = Entity(parent=level_editor)
#         self.size = 16
#         self.grid = Entity(parent=self, model=Grid(self.size,self.size), rotation_x=90, scale=32, color=color.white33)
#         for x in range(self.size):
#             for y in range(self.size):
#                 Entity(parent=self.asset_scene, model='cube', collider='box', color=color.random_color())
#
#
#
#
#     def input(self, key):
#         if key == 'tab':
#             level_editor.enabled = not level_editor.enabled
#             self.asset_scene.enabled = not self.asset_scene.enabled

class ModelChanger(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=level_editor)
        self.model_names = [e.stem for e in application.internal_models_compressed_folder.glob('**/*.ursinamesh')]
        for file_type in ('.bam', '.obj', '.ursinamesh'):
            self.model_names += [e.stem for e in application.asset_folder.glob(f'**/*.{file_type}') if not 'animation' in e]


    def input(self, key):
        if key == 'm' and level_editor.selection:
            current_model_index = self.model_names.index(level_editor.selection[-1].model.name)
            print('current model:', self.model_names[current_model_index])
            for e in level_editor.selection:
                e.model = self.model_names[current_model_index+1]

class Help(Button):
    def __init__(self, **kwargs):
        super().__init__(parent=level_editor.ui, text='?', scale=.025, model='circle', origin=(-.5,.5), position=window.top_left)
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
    def __init__(self, **kwargs):
        super().__init__()
        self.dragger = Draggable(parent=scene, model='plane', plane_direction=(0,1,0), enabled=False)
        def drop(self=self):
            for e in self.dragger.children:
                e.world_parent = e.original_parent

            self.dragger.enabled = False
            selector.render_selection()

        self.dragger.drop = drop

    def input(self, key):
        if held_keys['shift'] and key == 'd' and level_editor.selection:
            self.dragger.position = level_editor.selection[-1].world_position

            for e in level_editor.selection:
                clone = duplicate(e, original_parent=e.parent, color=e.color, shader=e.shader, origin=e.origin, world_parent=self.dragger)
                level_editor.entities.append(clone)

            level_editor.selection.clear()
            level_editor.selection = self.dragger.children
            selector.render_selection()
            self.dragger.enabled = True
            self.dragger.start_dragging()
            gizmo.enabled = False


class PrimitiveMenu(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=level_editor)
        self.menu_parent = Entity(parent=level_editor.ui, z=-1, enabled=0)
        for name in ('cube', 'plane', 'sphere', 'diamond'):
            b = Button(parent=self.menu_parent, text=name, scale=.1, is_gizmo=True)
            def set_model(name=name):
                for e in level_editor.selection:
                    e.model = name
                    e.origin = e.origin
                    self.menu_parent.enabled = False
                    selector.render_selection()
            b.on_click = set_model

        grid_layout(self.menu_parent.children, max_x=2)


    def input(self, key):
        if key == 'left mouse down' and not mouse.hovered_entity in self.menu_parent.children:
            self.menu_parent.enabled = False

        if key == 'v' and level_editor.selection:
            self.menu_parent.position = mouse.position.xy
            self.menu_parent.enabled = True




if __name__ == '__main__':
    app = Ursina(vsync=False)

level_editor = LevelEditor()

DirectionalLight(parent=level_editor).look_at(Vec3(-1,-1,-1))

for x in range(8):
    for y in range(8):
        level_editor.scenes[x][y].undo = Undo()

gizmo = Gizmo()
scale_gizmo = ScaleGizmo()
gizmo_toggler = GizmoToggler(parent=level_editor)

QuickGrabber(parent=level_editor)   # requires gizmo, scale_gizmo, gizmo_toggler, selector
selector = Selector(parent=level_editor)
SelectionBox(parent=level_editor.ui, model=Quad(0, mode='line'), origin=(-.5,-.5,0), scale=(0,0,1), color=color.white33, mode='new')
Spawner(parent=level_editor)
Duplicator()
LevelMenu()
# ModelChanger()
PrimitiveMenu()
# PointOfViewSelector()
Help()

def input(key):
    if key == 'q':
        print(level_editor.entities)

t = Text(position=window.top_left + Vec2(.01,-.06))
def update():
    t.text = 'selection:\n' + '\n'.join([str(e) for e in level_editor.selection])

if __name__ == '__main__':
    app.run()
