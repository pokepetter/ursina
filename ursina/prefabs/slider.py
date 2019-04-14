from ursina import *


class Slider(Entity):
    def __init__(self, min=0, max=1, default=0, **kwargs):
        super().__init__()
        self.parent = camera.ui
        self.vertical = False
        self.min = min
        self.max = max
        self.default = default
        self.step = 0

        self.label = Text(parent=self, origin=(0.5, 0), x=-0.025, text='label')
        self.bg = Button(
            parent = self,
            model = Quad(scale=(.525,.025), radius=.01, segments=3),
            origin_x = -0.25
            )


        self.bg.on_click = '''
            self.parent.knob.x = mouse.point[0] * self.scale_x
            self.parent.knob.dragging = True
            '''

        self.knob = Draggable(
            parent = self,
            min_x = 0,
            max_x = .5,
            min_y = 0,
            max_y = .5,
            step = self.step,
            world_parent = self,
            model = 'sphere',
            collider = 'sphere',
            color = color.light_gray,
            world_scale = .5,
            text = "0",
            )


        def drop():
            # print('yo', self.parent)
            if hasattr(self, 'on_value_changed'):
                self.on_value_changed()

        self.knob.drop = drop
        self.value = self.default
        self.dynamic = True


        self.knob.text_entity.text = str(round(self.default, 2))

        for key, value in kwargs.items():
            setattr(self, key, value)

        if self.vertical:
            self.rotation_z = -90
            self.label.rotation_z = 90
            self.label.origin = (0,0)
            self.knob.lock_x = True
            self.knob.text_entity.rotation_z = 90
            self.knob.text_entity.y = -2
        else:
            self.knob.lock_y = True
            self.knob.text_entity.y = 1


    @property
    def value(self):
        return lerp(self.min, self.max, self.knob.x * 2)

    @value.setter
    def value(self, value):
        self.knob.x = value / (self.max - self.min) / 2
        self._prev_value = self.knob.x / self.bg.scale_x

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        self._step = value / (self.max-self.min) / 2
        self.knob.step = self._step

    def update(self):
        if self.knob.dragging:
            t = self.knob.x / .5
            self.knob.text_entity.text = round(lerp(self.min, self.max, t), 2)

            if self.dynamic and hasattr(self, 'on_value_changed') and self._prev_value != t:
                self.on_value_changed()
                self._prev_value = t


    # def on_value_changed(self):
    #     print('changed', self.value)


if __name__ == '__main__':
    app = Ursina()
    origin = Entity(model='cube', color=color.green, scale = .05)
    slider = Slider(0, 12, default=1, scale=1, y=-.4, step=1, vertical=True)
    # slider.value = 2
    app.run()
