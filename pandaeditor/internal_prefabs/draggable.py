from pandaeditor import *

class Draggable(Button):

    def __init__(self, **kwargs):
        super().__init__()
        self.require_key = None
        self.dragging = False
        self.start_pos = self.position

        self.x_lock = False
        self.y_lock = False
        self.min_x, self.min_y, self.min_z = -math.inf, -math.inf, -math.inf
        self.max_x, self.max_y, self.max_z = math.inf, math.inf, math.inf

        for key, value in kwargs.items():
            setattr(self, key, value)


    def input(self, key):
        # super().input(key)

        if self.hovered and key == 'left mouse down':
            if not self.require_key or held_keys[self.require_key]:
                self.dragging = True
                self.start_pos = self.position
                try:
                    self.drag()
                except:
                    pass

        if self.dragging and key == 'left mouse up':
            self.dragging = False
            self.delta_drag = self.position - self.start_pos
            try:
                self.drop()
            except:
                print('no drop func')
                pass

    # def drag(self):
    #     print('start drag test')
    #
    # def drop(self):
    #     print('drop test')

    def update(self, dt):
        if self.dragging:
            # make drag work event when parented to scaled entity
            # if self.parent and isinstance(self.parent, Entity):
            #     if not self.x_lock:
            #         self.world_x += mouse.velocity[0] * camera.fov * self.parent.world_scale_x
            #     if not self.y_lock:
            #         self.world_y += mouse.velocity[1] * camera.fov * self.parent.world_scale_y
            # else:
            if not self.x_lock:
                self.world_x += mouse.velocity[0] * camera.fov
            if not self.y_lock:
                self.world_y += mouse.velocity[1] * camera.fov

        self.position = (
            clamp(self.x, self.min_x, self.max_x),
            clamp(self.y, self.min_y, self.max_y),
            clamp(self.z, self.min_z, self.max_z)
            )

if __name__ == '__main__':
    app = PandaEditor()
    camera.orthographic = True

    e = Draggable()
    e.parent = scene
    # e.require_key = 'shift'
    app.run()
