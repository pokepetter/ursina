from ursina import *


class Slider(Entity):
    def __init__(self, min=0, max=1, default=0, **kwargs):
        super().__init__()
        self.parent = camera.ui
        self.min = min
        self.max = max
        self.default = default

        self.label = Text(parent=self, origin=(0.5, 0), x=-0.025, text="label")
        self.bg = Button(parent=self, scale_y=0.01, scale_x=0.5, origin_x=-0.5)
        self.bg.on_click = """
            self.parent.knob.x = mouse.point[0] * self.scale_x
            self.parent.knob.dragging = True
            """

        self.knob = Draggable(
            parent = self,
            lock_y = True,
            min_x = 0,
            max_x = self.bg.scale_x,
            world_parent = self,
            model = "sphere",
            collider = "sphere",
            color = color.light_gray,
            world_scale = Vec3(1, 1, 1) * 0.5,
            text = "0",
            )
        self.knob.text_entity.y = 1
        def drop():
            # print('yo', self.parent)
            if hasattr(self, "on_value_changed"):
                self.on_value_changed()
        self.knob.drop = drop
        self.value = self.default

        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def value(self):
        return self.knob.x * 2

    @value.setter
    def value(self, value):
        self.knob.x = value / (self.max - self.min) / 2
        if hasattr(self, "on_value_changed"):
            self.on_value_changed()

    def update(self):
        if self.knob.dragging:
            t = self.knob.x / self.bg.scale_x
            self.knob.text_entity.text = round(lerp(self.min, self.max, t), 2)


if __name__ == "__main__":
    app = Ursina()
    slider = Slider(0, 3, default=1)
    # slider.value = 2
    app.run()
