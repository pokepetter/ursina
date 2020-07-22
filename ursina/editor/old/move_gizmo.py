from ursina import *


class MoveGizmo(Entity):
    def __init__(self, parent=scene, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.name = 'move gizmo'
        self.description = 'move with gizmo'
        self.hotkeys = ['w', ]

        self.scene_editor = parent
        self.gizmo_parent = Entity(parent=self, always_on_top=True, enabled=False) # enable when selecting something
        self.gizmo_parts = list()
        self.origin_indicator = Draggable(parent=self.gizmo_parent, model='sphere', scale=.075, color=color.white, always_on_top=True, drag=self.drag, drop=self.drop)
        self.gizmo_parts.append(self.origin_indicator)

        for i, col in enumerate((color.magenta, color.yellow, color.cyan)):
            arrow = Draggable(parent=self.gizmo_parent, model='cube', color=col, scale=(.05,.05,1), origin_z=-.5, lock_x=True, lock_y=True, lock_z=True)
            arrow.collider = BoxCollider(arrow, (0,0,.5), (2,2,1))
            arrow.look_at((Vec3(1,0,0), Vec3(0,1,0), Vec3(0,0,1))[i])
            arrow.position += arrow.forward * .2
            arrow.plane_direction = (Vec3(0,0,1), Vec3(0,0,1), Vec3(0,1,0))[i]
            setattr(arrow, ('lock_x', 'lock_y', 'lock_z')[i], False)
            arrow.name = col.name + '_arrow'
            arrow.highlight_color = color.black
            arrow.drag_color = color.black
            self.gizmo_parts.append(arrow)

            arrow.drag = self.drag
            arrow.drop = self.drop

        self.h_plane = Draggable(parent=self.gizmo_parent, model='cube', color=lerp(color.magenta, color.cyan, .5), scale=(.25,.01,.25), origin=(-.75,-.5,-.75), always_on_top=True, lock_x=True, lock_y=True, lock_z=True)
        for gizmo in self.gizmo_parts:
            gizmo.original_position = gizmo.position
            gizmo.original_scale = gizmo.scale


    def update(self):
        if self.gizmo_parent.enabled:
            self.gizmo_parent.scale = distance(self, camera) * .05


    def drag(self):
        dragged_part = [e for e in self.gizmo_parts if e.dragging]
        if not dragged_part:
            return
        dragged_part = dragged_part[0]
        dragged_part.plane_direction = camera.world_position - dragged_part.world_position

        dragged_part.world_parent = scene
        self.world_parent = dragged_part
        for gizmo in self.gizmo_parts:
            if not gizmo == dragged_part:
                gizmo.collision = False

        for e in self.scene_editor.selection:
            e.original_parent = e.parent
            e.world_parent = self
            e.collision = False

        # if dragged_part == self.origin_indicator:
        #     dragged_part.



    def drop(self):
        self.world_parent = self.scene_editor
        for gizmo in self.gizmo_parts:
            gizmo.parent = self.gizmo_parent
            gizmo.position = gizmo.original_position
            gizmo.scale = gizmo.original_scale
            gizmo.collision = True

        for e in self.scene_editor.selection:
            e.world_parent = e.original_parent
            e.collision = True

        print('DROP')


    def input(self, key):
        if key == 'left mouse down' and not mouse.hovered_entity:
            self.scene_editor.selection = list()
            self.gizmo_parent.enabled = False

        if key == 'left mouse down' and mouse.hovered_entity in self.scene_editor.entities:
            mouse_hits = [e.entity for e in mouse.collisions]
            # print(mouse_hits)
            for e in self.gizmo_parts:
                if e in mouse_hits:
                    e.start_dragging()
                    return

            self.scene_editor.selection = [mouse.hovered_entity, ]
            self.gizmo_parent.enabled = True

            self.world_position = self.scene_editor.selection[-1].position
            print(self.scene_editor.selection)




if __name__ == '__main__':
    app = Ursina()
    dummy = Entity()
    dummy.entities = [
        Button(parent=scene, model='cube', color=color.light_gray, texture='white_cube', highlight_color=color.light_gray, pressed_color=color.light_gray, name='ofijeoif'),
        Button(parent=scene, model='plane', color=color.lime, scale=8, collider='box')
        ]
    dummy.selection = list()
    MoveGizmo(parent=dummy)
    Sky(color=color.dark_gray)
    EditorCamera()
    app.run()
