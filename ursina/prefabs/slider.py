from ursina import *


class Slider(Entity):
    def __init__(self, min=0, max=1, default=0, height=Text.size, text='', dynamic=False, **kwargs):
        super().__init__()
        self.parent = camera.ui
        self.vertical = False
        self.min = min
        self.max = max
        self.default = default
        self.step = 0

        self.label = Text(parent=self, origin=(0.5, 0), x=-0.025, text=text)
        self.bg = Button(
            parent = self,
            model = Quad(scale=(.525, height), radius=Text.size/2, segments=3),
            origin_x = -0.25,
            pressed_scale = 1,
            highlight_color = Button.color,
            pressed_color = Button.color,
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
            model = Quad(radius=Text.size/2, scale=(Text.size, height)),
            collider = 'box',
            color = color.light_gray,
            text = "0",
            text_origin = (0, -.55),
            z = -.1
            )


        def drop():
            # print('yo', self.parent)
            if hasattr(self, 'on_value_changed'):
                self.on_value_changed()

        self.knob.drop = drop
        self.value = self.default
        self.dynamic = dynamic


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
            self.knob.text_entity.y = height/2


    @property
    def value(self):
        val = lerp(self.min, self.max, self.knob.x * 2)
        if self.step == 1:
            val = round(val)

        return val

    @value.setter
    def value(self, value):
        self.knob.x = value / (self.max - self.min) / 2
        self._prev_value = self.knob.x / self.bg.scale_x

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        self._step = value
        self.knob.step = value / (self.max-self.min) / 2

    def update(self):
        if self.knob.dragging:
            t = self.knob.x / .5
            self.knob.text_entity.text = round(lerp(self.min, self.max, t), 2)

            if isinstance(self.step, int) or self.step.is_integer():
                self.knob.text_entity.text = str(self.value)

            if self.dynamic and hasattr(self, 'on_value_changed') and self._prev_value != t:
                self.on_value_changed()
                self._prev_value = t

    def __setattr__(self, name, value):
        if name == 'eternal':
            try:
                self.label.eternal = value
                self.bg.eternal = value
                self.knob.eternal = value
            except:
                pass
        try:
            super().__setattr__(name, value)
        except Exception as e:
            return e


if __name__ == '__main__':
    app = Ursina()
    origin = Entity(model='cube', color=color.green, scale = .05)
    box = Entity(model='cube', origin_y=-.5, scale=1, color=color.orange)
    slider = Slider(0, 12, default=1, height=Text.size*3, y=-.4, step=.1, vertical=False)

    def scale_box():
        box.scale_y = slider.value

    slider.on_value_changed = scale_box
    app.run()
