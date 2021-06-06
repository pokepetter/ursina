from ursina import *
from ursina.shaders import lit_with_shadows_shader, unlit_shader


app = Ursina()

class LevelEditor(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.entities = []
        self.selection = []
        self.grid = Entity(parent=self, model=Grid(16,16), rotation_x=90, scale=32, collider='box', color=color.white33)
        self.origin_mode = 'center'
        self.origin_mode_menu = ButtonGroup(['last', 'center', 'individual'], min_selection=1, position=window.top)
        self.editor_camera = EditorCamera(parent=self)
        self.ui = Entity(parent=camera.ui)
        self.on_enable = Func(self.ui.enable)
        self.on_disable = Func(self.ui.disable)



level_editor = LevelEditor()

DirectionalLight(parent=level_editor).look_at(Vec3(-1,-1,-1))

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


undo = Undo()


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

# if not load_model('scale_gizmo'):
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
        undo.record_undo(changes)


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


gizmo = Gizmo()


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

        undo.record_undo(changes)
        self.dragging = False
        self.scaler.scale = 1



    def update(self):
        if self.dragging:
            if not level_editor.origin_mode_menu.value[0] == 'individual':
                self.scaler.scale += Vec3(sum(mouse.velocity), sum(mouse.velocity), sum(mouse.velocity)) * 100 * time.dt * self.axis
            else:
                for e in level_editor.selection:
                    e.scale += Vec3(sum(mouse.velocity), sum(mouse.velocity), sum(mouse.velocity)) * 100 * time.dt * self.axis

scale_gizmo = ScaleGizmo()


# class RotationGizmo(Entity):



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

gizmo_toggler = GizmoToggler(parent=level_editor)



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

        if key in self.gizmos_to_toggle.keys() and not held_keys['control']:
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



QuickGrabber(parent=level_editor)




class Selector(Entity):
    def input(self, key):
        if key == 'left mouse down':
            for e in level_editor.entities:
                e.collision = True

            if hasattr(mouse.hovered_entity, 'is_gizmo'):
                return
                print('clicked on gizmo')

            # wait one frame to get hovered entity so the colliders are turned on
            invoke(self.select_hovered_entity, delay=1/60)

        elif key == 'left mouse up':
            for e in level_editor.entities:
                e.collision = False


    def select_hovered_entity(self, enable_gizmo=True):
        clicked_entity = mouse.hovered_entity
        if clicked_entity in level_editor.entities and not clicked_entity in level_editor.selection and not held_keys['alt']:
            if held_keys['shift']:
                level_editor.selection.append(clicked_entity) # append
            else:
                level_editor.selection = [clicked_entity, ]   # overwrite

        if held_keys['alt'] and clicked_entity in level_editor.selection:
            level_editor.selection.remove(clicked_entity) # remove
            # return

        if not clicked_entity and not held_keys['shift'] and not held_keys['alt']: # clear
            level_editor.selection.clear()

        self.render_selection()


    def render_selection(self):
        for e in level_editor.entities:
            if e in level_editor.selection:
                e.color = color.azure
            else:
                e.color = color.white

        gizmo.enabled = bool(level_editor.selection)

        if level_editor.selection:
            print(level_editor.origin_mode_menu.value, level_editor.origin_mode_menu.value[0] in ('last', 'individual'), level_editor.selection)
            if level_editor.origin_mode_menu.value[0] in ('last', 'individual'):
                gizmo.position = level_editor.selection[-1].position
            else: # center
                gizmo.position = sum([e.position for e in level_editor.selection]) / len(level_editor.selection)
        # level_editor.selection = []
        # gizmo.enabled = False


t = Text(position=window.top_left + Vec2(.01,-.06))
def update():
    t.text = 'selection:\n' + '\n'.join([str(e) for e in level_editor.selection])

    # t.text += '\n\ngizmo arrow parent:' + str(gizmo.arrows[0].parent)


selector = Selector(parent=level_editor)


class SelectionBox(Entity):
    def input(self, key):
        if key == 'left mouse down':
            if mouse.hovered_entity and not mouse.hovered_entity in level_editor.selection:
                print('-------', 'clicked on gizmo, dont box select')
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
                    if self.mode != 'subtract' and not e in level_editor.selection:
                        level_editor.selection.append(e)

                    elif e in level_editor.selection:
                        level_editor.selection.remove(e)

            selector.render_selection()
            self.mode = 'new'

    def update(self):
        if mouse.left:
            if mouse.x == mouse.start_x and mouse.y == mouse.start_y:
                return

            self.scale_x = mouse.x - self.x
            self.scale_y = mouse.y - self.y

SelectionBox(parent=level_editor.ui, model=Quad(0, mode='line'), origin=(-.5,-.5,0), scale=(0,0,1), color=color.white33, mode='new')


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
                color=color.white,
                position=mouse.world_point,
                collision=False,
                )
            level_editor.entities.append(self.target)

        elif key == 'n up':
            # self.target.collision = True
            self.target = None
            level_editor.grid.collision = False

    def update(self):
        if held_keys['n'] and mouse.world_point and self.target:
            self.target.position = mouse.world_point
Spawner(parent=level_editor)


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


camera.clip_plane_near = 2
camera.clip_plane_far = 200
from ursina.shaders import ssao_shader
camera.shader = ssao_shader


PointOfViewSelector()

class AssetBrowser(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=level_editor)
        self.menu = Entity(parent=level_editor.ui, model=Quad(radius=.05), color=color.black, scale=.2, origin=(.5,0), x=camera.aspect_ratio*.495, collider='box')
        self.menu.grid = Entity(parent=self.menu, model=Grid(8,8), z=-1, origin=self.menu.origin, color=color.dark_gray)
        self.cursor = Entity(parent=self.menu, scale=1/8, model='quad', color=color.azure, origin=(-.5,-.5))
        self.tabs = [Button(parent=self.menu, scale=(1/4,1/8), position=(-1+(i/4),.5), origin=(-.5,-.5), color=color.hsv(90*i,.5,.3)) for i in range(4)]

    def update(self):
        self.cursor.enabled = self.menu.hovered
        if self.menu.hovered:
            grid_pos = [floor(mouse.point.x * 8) / 8, floor(mouse.point.y * 8) / 8]
            self.cursor.position = grid_pos


    def input(self, key):
        if key == 'm':
            self.menu.enabled = not self.menu.enabled

        if key == 'left mouse down' and self.menu.hovered:

            if not held_keys['shift'] and not held_keys['alt']:
                print('go to level')

            if held_keys['shift'] and not held_keys['alt']:
                print('add level')

            if held_keys['alt'] and not held_keys['shift']:
                print('unload level')


    # def on_click(self):
    #     print('a')
    #     self.cursor.position = mouse.point


AssetBrowser()

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
                f:          move the point the camera rotates around to target
                shift+f:    reset the point camera rotates around to (0,0,0)
            ''').strip(),
            background=True
        )

Help()

app.run()
