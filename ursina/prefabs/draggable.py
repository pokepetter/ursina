from ursina import *

class Draggable(Button):

    _z_plane = Entity(name='_z_plane', model='quad', collider='box', scale=(999,999),
        color=color.clear, enabled=False, eternal=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.require_key = None
        self.dragging = False
        self.delta_drag = 0
        self.start_pos = self.world_position
        self.start_offset = (0,0)
        self.step = (0,0)
        self.lock_x = False
        self.lock_y = False
        self.min_x, self.min_y, self.min_z = -math.inf, -math.inf, -math.inf
        self.max_x, self.max_y, self.max_z = math.inf, math.inf, math.inf



        for key, value in kwargs.items():
            if key == 'text':
                continue
            setattr(self, key, value)


    def input(self, key):
        if self.hovered and key == 'left mouse down':
            if self.require_key == None or held_keys[self.require_key]:
                self.start_dragging()

        if self.dragging and key == 'left mouse up':
            self.stop_dragging()

    def start_dragging(self):
        Draggable._z_plane.world_position = self.world_position
        if self.has_ancestor(camera.ui):
            Draggable._z_plane.world_parent = camera.ui
        else:
            Draggable._z_plane.world_parent = scene

        self.start_offset = mouse.world_point - self.world_position
        self.dragging = True
        self.start_pos = self.world_position
        self.collision = False
        self._z_plane.enabled = True
        try:
            self.drag()
        except:
            pass

    def stop_dragging(self):
        self.dragging = False
        self.delta_drag = self.world_position - self.start_pos
        self._z_plane.enabled = False
        self.collision = True

        if hasattr(self, 'drop'):
            self.drop()

    # def drag(self):
    #     print('start drag test')
    #
    # def drop(self):
    #     print('drop test')

    def update(self):
        if self.dragging:
            if mouse.world_point:
                if not self.lock_x:
                    self.world_x = mouse.world_point[0] - self.start_offset[0]
                if not self.lock_y:
                    self.world_y = mouse.world_point[1] - self.start_offset[1]

            if self.step[0] > 0 or self.step[1] > 0:
                hor_step = 1/self.step[0]
                ver_step = 1/self.step[1]
                self.x = round(self.x * hor_step) /hor_step
                self.y = round(self.y * ver_step) /ver_step

        self.position = (
            clamp(self.x, self.min_x, self.max_x),
            clamp(self.y, self.min_y, self.max_y),
            clamp(self.z, self.min_z, self.max_z)
            )


    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        if isinstance(value, (int, float, complex)):
            value = (value, value)

        self._step = value



if __name__ == '__main__':
    app = Ursina()
    camera.orthographic = True

    e = Draggable(scale=10)
    e.parent = scene
    # e.require_key = 'shift'
    app.run()
