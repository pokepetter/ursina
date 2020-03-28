from ursina import *



class MoveToPointTool(Entity):
    def __init__(self, parent, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.name = 'move to point'
        self.description = 'move_to_point'
        self.target = None
        self.target_start_pos = None
        self.offset = None

        self.hotkeys = ['v', ]



    def input(self, key):
        if key == 'left mouse down' and mouse.hovered_entity and mouse.hovered_entity in self.parent.entities:
            self.target = mouse.hovered_entity

            self.parent.world_plane.enabled = False
            self.target.collision = False

            self.target_start_pos = self.target.world_position
            self.offset = self.target.world_position - mouse.world_point

        if key == 'left mouse up' and self.target:
            self.target.collision = True

            # undo_cache.append(Func(setattr, self.move_target, 'world_position', self.move_target.original_position))
            self.target = None



    def update(self):
        if not self.target:
            return

        self.target.world_position = mouse.world_point + self.offset

        if held_keys['control']:
            self.target.world_position = round(self.target.world_position, 1)
