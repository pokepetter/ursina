from ursina import *



class ScaleTool(Entity):
    def __init__(self, parent, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.name = 'scale tool'
        self.description = 'scale'
        self.target = None
        self.hotkeys = ['e', 's']

        # mouse_velocity = (mouse.velocity[0] + mouse.velocity[1])
        # if held_keys['e'] or held_keys['s']:
        #     self.move_target.scale += Vec3(
        #         self.move_target.scale_x * mouse_velocity,
        #         self.move_target.scale_y * mouse_velocity,
        #         self.move_target.scale_z * mouse_velocity
        #         ) * 5


    def input(self, key):
        if key == 'left mouse down' and mouse.hovered_entity and mouse.hovered_entity in self.parent.entities:
            self.target = mouse.hovered_entity

        if key == 'left mouse up' and self.target:
            # undo_cache.append(Func(setattr, self.move_target, 'world_position', self.move_target.original_position))
            self.target = None


    def update(self):
        if not self.target:
            return
        # if self.tool == 'move_x_z':
        mouse_velocity = (mouse.velocity[0] + mouse.velocity[1])

        self.target.world_scale += Vec3(
                self.target.scale_x * mouse_velocity,
                self.target.scale_y * mouse_velocity,
                self.target.scale_z * mouse_velocity
                ) * 5
        # self.target.world_position = Vec3(mouse.world_point[0], self.target.y, mouse.world_point[2]) + self.offset
        if held_keys['control']:
            self.target.world_scale = round(self.target.world_position, 1)
