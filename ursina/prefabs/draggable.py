from ursina import *

class Draggable(Button):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.require_key = None
        self.dragging = False
        self.start_pos = self.world_position
        self.step = 0
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
            if not self.require_key or held_keys[self.require_key]:
                self.dragging = True
                self.start_pos = self.world_position
                try:
                    self.drag()
                except:
                    pass

        if self.dragging and key == 'left mouse up':
            self.dragging = False
            self.delta_drag = self.position - self.world_position
            try:
                self.drop()
            except:
                # print('no drop func')
                pass

    # def drag(self):
    #     print('start drag test')
    #
    # def drop(self):
    #     print('drop test')

    def update(self):
        if self.dragging:
            if not self.lock_x:
                self.world_x = self.start_pos[0] + (mouse.delta[0] * camera.fov * camera.aspect_ratio)
            if not self.lock_y:
                self.world_y = self.start_pos[1] + (mouse.delta[1] * camera.fov)

            if self.step > 0:
                r = 1/self.step
                self.x = round(self.x * r) /r
                self.y = round(self.y * r) /r

        self.position = (
            clamp(self.x, self.min_x, self.max_x),
            clamp(self.y, self.min_y, self.max_y),
            clamp(self.z, self.min_z, self.max_z)
            )



if __name__ == '__main__':
    app = Ursina()
    camera.orthographic = True

    e = Draggable()
    # e.parent = scene
    # e.require_key = 'shift'
    app.run()
