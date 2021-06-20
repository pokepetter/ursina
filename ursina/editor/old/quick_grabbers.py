class BoxQuickScaler(Entity):
    def __init__(self, **kwargs):
        super().__init__(model='wireframe_cube', color=color.azure, visible=False, parent=level_editor)

    def input(self, key):
        if key == 'left mouse down':
            if not mouse.hovered_entity in level_editor.entities:
                self.visible = False
                return

            self.target = mouse.hovered_entity
            self.visible = True
            self.transform = self.target.world_transform


def quick_select(attr):
    level_editor.selection.clear()
    gizmo.visible = False
    selector.input('left mouse down')
    # print('quick select', level_editor.selection)
    if level_editor.selection:
        setattr(level_editor.selection[0], f'_original_{attr}', getattr(level_editor.selection[0], attr))

def quick_deselect(attr):
    if level_editor.selection:
        undo.record_undo([[level_editor.selection[0], attr, getattr(level_editor.selection[0], f'_original_{attr}'), getattr(level_editor.selection[0], attr)], ])
        setattr(level_editor.selection[0], f'_original_{attr}', None)

    selector.input('left mouse up')
    level_editor.selection.clear()
    selector.render_selection()
    gizmo.visible = True


class QuickScaler(Entity):
    def input(self, key):
        if key == self.hotkey:                                          quick_select(self.attr)
        elif key == self.hotkey + ' up' and level_editor.selection:     quick_deselect(self.attr)


    def update(self):
        if held_keys[self.hotkey] and not held_keys['control'] and level_editor.selection:
            if not hasattr(level_editor.selection[0], f'_original_{self.attr}') or not getattr(level_editor.selection[0], f'_original_{self.attr}'):
                setattr(level_editor.selection[0], f'_original_{self.attr}', getattr(level_editor.selection[0], self.attr))

            level_editor.selection[0].scale += Vec3(sum(mouse.velocity), sum(mouse.velocity), sum(mouse.velocity)) * 100 * time.dt
scaler = QuickScaler(parent=level_editor, attr='scale', hotkey='s')


class QuickRotator(Entity):
    def input(self, key):
        if key == self.hotkey:                                          quick_select(self.attr)
        elif key == self.hotkey + ' up' and level_editor.selection:     quick_deselect(self.attr)

    def update(self):
        if held_keys[self.hotkey] and not held_keys['control'] and level_editor.selection:
            if not hasattr(level_editor.selection[0], f'_original_{self.attr}') or not getattr(level_editor.selection[0], f'_original_{self.attr}'):
                setattr(level_editor.selection[0], f'_original_{self.attr}', getattr(level_editor.selection[0], self.attr))

            level_editor.selection[0].rotation_y -= sum(mouse.velocity) * 6400 * time.dt
QuickRotator(parent=level_editor, attr='rotation', hotkey='r')


quick_grab_gizmo = Draggable(parent=level_editor, model='cube', color=color.red, plane_direction=(0,1,0), scale=1.1, enabled=False, always_on_top=True)

class QuickGrabber(Entity):  # hold g to move hovered entity
    def input(self, key):
        if key == self.hotkey:
            quick_select(self.attr)

        elif key == self.hotkey + ' up' and level_editor.selection:
            quick_grab_gizmo.stop_dragging()
            level_editor.selection[0].world_parent = scene
            quick_deselect(self.attr)
            quick_grab_gizmo.enabled = False

    def update(self):
        if held_keys[self.hotkey] and not held_keys['control'] and level_editor.selection:
            if not level_editor.selection[0].parent == quick_grab_gizmo:
                if not hasattr(level_editor.selection[0], f'_original_{self.attr}') or not getattr(level_editor.selection[0], f'_original_{self.attr}'):
                    setattr(level_editor.selection[0], f'_original_{self.attr}', getattr(level_editor.selection[0], self.attr))

                quick_grab_gizmo.enabled = True
                quick_grab_gizmo.position = level_editor.selection[0].position
                level_editor.selection[0].world_parent = quick_grab_gizmo
                quick_grab_gizmo.start_dragging()


quick_grabber = QuickGrabber(parent=level_editor, attr='world_position', hotkey='g')

class QuickGrabberAxisToggler(Entity):
    def input(self, key):
        if key in ('g', 'x', 'y', 'z') and not held_keys['control']:
            if not quick_grabber.hotkey == key:
                quick_grabber.input(quick_grabber.hotkey + ' up'),

            quick_grabber.hotkey = key
            if key == 'g':
                quick_grab_gizmo.lock = Vec3(0,1,0)
                quick_grab_gizmo.plane_direction = Vec3(0,1,0)
            elif key == 'x':
                quick_grab_gizmo.lock = Vec3(0,1,1)
                quick_grab_gizmo.plane_direction = Vec3(0,1,0)
            elif key == 'z':
                quick_grab_gizmo.lock = Vec3(1,1,0)
                quick_grab_gizmo.plane_direction = Vec3(0,1,0)
            elif key == 'y':
                quick_grab_gizmo.lock = Vec3(1,0,1)
                quick_grab_gizmo.plane_direction = Vec3(0,0,1)

            quick_grabber.input(key)

QuickGrabberAxisToggler(parent=level_editor)
