from ursina import *
from ursina.shaders import lit_with_shadows_shader


class LevelEditor(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.grid = Entity(model=Grid(16,16), rotation_x=90, scale=32, original_y=0, collider='box', color=color.white33)
        self.entities = []
        self.target = None

        # input_handler.bind('g', 'left mouse down')

        # self.tool = 'grab'
        self.gizmo = Draggable(parent=self, model='cube', color=color.orange, scale=.25, enabled=False, always_on_top=True, shader=lit_with_shadows_shader)
        self.selection = []
        self.origin_mode = 'center'
        self.origin_mode_menu = ButtonGroup(['last', 'center', 'individual'], min_selection=1, position=window.top)


    def update(self):
        if not self.selection:
            return

        if held_keys['s'] and not held_keys['control']:
            targets = self.selection
            if self.origin_mode_menu.value != 'individual':
                targets = [self.gizmo, ]

            for e in targets:
                e.scale += Vec3(sum(mouse.velocity), sum(mouse.velocity), sum(mouse.velocity)) * 100 * time.dt

        if held_keys['r'] and not held_keys['control']:
            targets = self.selection
            if self.origin_mode_menu.value != 'individual':
                targets = [self.gizmo, ]

            for e in targets:
                e.rotation_y -= sum(mouse.velocity) * 6400 * time.dt


    def input(self, key):
        if key == 'left mouse down':
            if not mouse.hovered_entity:
                self.selection = []

            elif mouse.hovered_entity in self.selection:
                self.selection.remove(mouse.hovered_entity)

            elif mouse.hovered_entity in self.entities:
                if held_keys['shift']:
                    self.selection.append(mouse.hovered_entity)
                else:
                    self.selection = [mouse.hovered_entity, ]

            for e in self.entities:
                e.color = color.azure if e in self.selection else color.light_gray
            self.gizmo.enabled = bool(self.selection)
            if self.selection:
                self.gizmo.position = self.selection[-1].position

                print(self.origin_mode_menu.value)
                if self.origin_mode_menu.value == 'center':
                    self.gizmo.position = sum(e.position for e in self.selection) / len(self.selection)


        # print(key)
        if key in ('s', 'r'):
            # if not self.selection and mouse.hovered_entity in self.entities:
            #     self.selection = [mouse.hovered_entity, ]
            for e in self.selection:
                e.world_parent = self.gizmo

        elif key in ('s up', 'r up'):
            for e in self.selection:
                e.world_parent = self


        # keys = ('s', 'x', 'y', 'z', 'r')
        # if key in keys and mouse.hovered_entity in self.entities:
        #     if not self.selection:
        #         self.selection = [mouse.hovered_entity, ]
        #
        #     for e in self.selection:
        #         e.world_parent = self.gizmo
        #     # mouse.hovered_entity.collision = False

        # elif key in [f'{e} up' for e in keys] and self.target:
        #     # self.target.collision = True
        #     # self.target.stop_dragging()
        #     self.selection = []

        # if key == 'x':
        #     for e in self.selection:
        #         e.plane_direction = Vec3(0,1,0)
        #         e.lock_y = True
        #         e.lock_z = True
        #         # e.start_dragging()
        # if key == 'y':
        #     for e in self.selection:
        #         e.plane_direction = Vec3(0,0,1)
        #         e.lock_x = True
        #         e.lock_z = True
        #         # e.start_dragging()
        # if key == 'z':
        #     for e in self.selection:
        #         e.plane_direction = Vec3(0,1,0)
        #         e.lock_x = True
        #         e.lock_y = True
        #         # e.start_dragging()


        if key == 'n':
            self.grid.collision = True
            invoke(self.add_entity, delay=.01)

        if key == 'd' and mouse.hovered_entity in self.entities:
            target = mouse.hovered_entity

            clone = self.add_entity()
            for name in ('position', 'rotation', 'scale', 'color', 'texture'):
                setattr(clone, name, getattr(target, name))

            clone.model = copy(target.model)
            clone.start_dragging()

        if held_keys['control'] and key == 'c' and mouse.hovered_entity in self.entities:
            self.entity_to_paste = {
                'rotation' : mouse.hovered_entity.rotation,
                'scale' : mouse.hovered_entity.scale,
                'color' : mouse.hovered_entity.color,
                'model_name' : mouse.hovered_entity.model.name,
            }
            if mouse.hovered_entity.texture:
                self.entity_to_paste['texture'] = mouse.hovered_entity.texture.name

        if held_keys['control'] and key == 'v' and self.entity_to_paste:
            self.grid.collision = True
            invoke(self.add_entity, *self.entity_to_paste.values(), delay=.01)



    def add_entity(self, rotation=(0,0,0), scale=1, color=color.gray, model='cube'):
        e = Entity(parent=self, model=model, collider='box', plane_direction=Vec3(0,1,0), position=mouse.world_point,
            rotation=rotation, scale=scale, color=color, highlight_color=color,
            shader=lit_with_shadows_shader,
            )
        self.entities.append(e)
        self.grid.collision = False
        return e




if __name__ == '__main__':
    app = Ursina()
    LevelEditor()
    EditorCamera()
    sun = DirectionalLight(y=50, rotation_x=120)
    sun._light.get_lens().set_near_far(0,30)

    sun._light.show_frustum()
    app.run()
