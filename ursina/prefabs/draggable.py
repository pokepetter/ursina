from ursina import *

class Draggable(Button):

    _z_plane = Entity(name='_z_plane', scale=(9999,9999), enabled=False, eternal=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.require_key = None
        self.dragging = False
        self.delta_drag = 0
        self.start_pos = self.world_position
        self.start_offset = (0,0,0)
        self.step = (0,0,0)
        self.plane_direction = (0,0,1)
        self.lock_x = False
        self.lock_y = False
        self.lock_z = False
        self.min_x, self.min_y, self.min_z = -inf, -inf, -inf
        self.max_x, self.max_y, self.max_z = inf, inf, inf

        if not Draggable._z_plane.model: # set these after game start so it can load the model
            Draggable._z_plane.model = 'quad'
            Draggable._z_plane.collider = 'box'
            Draggable._z_plane.color = color.clear


        for key, value in kwargs.items():
            if key == 'collider' and value == 'sphere' and self.has_ancestor(camera.ui):
                print('error: sphere colliders are not supported on Draggables in ui space.')

            if key == 'text' or key in self.attributes:
                continue

            setattr(self, key, value)


    def input(self, key):
        if self.hovered and key == 'left mouse down':
            if self.require_key == None or held_keys[self.require_key]:
                self.start_dragging()

        if self.dragging and key == 'left mouse up':
            self.stop_dragging()


    def start_dragging(self):
        Draggable._z_plane.world_position = mouse.world_point
        # Draggable._z_plane.world_position = self.world_position
        Draggable._z_plane.look_at(Draggable._z_plane.position - Vec3(*self.plane_direction))
        if self.has_ancestor(camera.ui):
            Draggable._z_plane.world_parent = camera.ui
        else:
            Draggable._z_plane.world_parent = scene

        self.start_offset = mouse.world_point - self.world_position
        self.dragging = True
        self.start_pos = self.world_position
        self.collision = False
        Draggable._z_plane.enabled = True
        mouse.traverse_target = Draggable._z_plane
        if hasattr(self, 'drag'):
            self.drag()


    def stop_dragging(self):
        self.dragging = False
        self.delta_drag = self.world_position - self.start_pos
        Draggable._z_plane.enabled = False
        self.collision = True
        mouse.traverse_target = scene

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
                if not self.lock_z:
                    self.world_z = mouse.world_point[2] - self.start_offset[2]

            if self.step[0] > 0:
                hor_step = 1/self.step[0]
                self.x = round(self.x * hor_step) /hor_step
            if self.step[1] > 0:
                ver_step = 1/self.step[1]
                self.y = round(self.y * ver_step) /ver_step
            if self.step[2] > 0:
                dep_step = 1/self.step[2]
                self.z = round(self.z * dep_step) /dep_step

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
            value = (value, value, value)

        self._step = value



if __name__ == '__main__':
    app = Ursina()

    Entity(model='plane', scale=8, texture='white_cube', texture_scale=(8,8))
    draggable_button = Draggable(scale=.1, text='drag me', position=(-.5, 0))
    world_space_draggable = Draggable(parent=scene, model='cube', color=color.azure, plane_direction=(0,1,0))

    EditorCamera(rotation=(30,10,0))
    world_space_draggable.drop = Func(print, 'dropped cube')

    app.run()
