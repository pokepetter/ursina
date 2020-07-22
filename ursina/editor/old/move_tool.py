from ursina import *



class MoveTool(Entity):
    def __init__(self, parent, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.name = 'move tool'
        self.description = 'move_x_z'
        self.target = None
        self.target_start_pos = None
        self.offset = None

        self.lock_axis = None
        self.ruler = Entity(parent=self, model='cube', scale=(.025,.025,9999), enabled=False, add_to_scene_entities=False)

        self.hotkeys = ['g', ]



    def input(self, key):
        if key == 'left mouse down' and mouse.hovered_entity and mouse.hovered_entity in self.parent.entities:
            self.target = mouse.hovered_entity

            self.parent.world_plane.rotation = (90,0,0)
            self.parent.world_plane.y = mouse.hovered_entity.world_y
            for e in self.parent.entities:
                e.collision = False

            self.target_start_pos = self.target.world_position
            self.offset = self.target.world_position - Vec3(mouse.world_point[0], self.target.y, mouse.world_point[2])
            if self.lock_axis:
                self.ruler.enabled = True
                self.ruler.world_position = self.target.world_position

        if key == 'left mouse up' and self.target:
            for e in self.parent.entities:
                e.collision = True

            # undo_cache.append(Func(setattr, self.move_target, 'world_position', self.move_target.original_position))
            self.target = None
            self.parent.world_plane.y = 0
            self.lock_axis = None
            self.ruler.enabled = False

        if key in ('x', 'y', 'z'):
            if key == self.lock_axis:
                self.lock_axis = None
            else:
                self.lock_axis = key

    @property
    def lock_axis(self):
        return self._lock_axis

    @lock_axis.setter
    def lock_axis(self, value):
        self._lock_axis = value
        print('lock:', value)
        if value == None:
            self.ruler.enabled = False
            return

        self.ruler.color = {'x':color.magenta, 'y':color.yellow, 'z':color.cyan}
        self.ruler.world_rotation = {'x':Vec3(0,-90,0), 'y':Vec3(90,0,0), 'z':Vec3(0,0,0)}


    def update(self):
        if not self.target:
            return
        # if self.tool == 'move_x_z':

        self.target.world_position = Vec3(mouse.world_point[0], self.target.y, mouse.world_point[2]) + self.offset
        if self.lock_axis == 'x':
            self.target.world_x = self.target_start_pos[0]
        if self.lock_axis == 'y':
            self.target.world_y = self.target_start_pos[1]
        if self.lock_axis == 'z':
            self.target.world_z = self.target_start_pos[2]

        if held_keys['control']:
            self.target.world_position = round(self.target.world_position, 1)
