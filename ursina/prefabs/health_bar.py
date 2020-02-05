from ursina import *


class HealthBar(Button):

    def __init__(self, max_value=100, show_text=True, show_lines=False, **kwargs):
        super().__init__(
            position = (-.45 * window.aspect_ratio, .45),
            origin = (-.5, .5),
            scale = (Text.size*20, Text.size),
            color = color.black66,
            highlight_color = color.black66,
            text = 'hp / max hp',
            ignore = True,
            )

        self.bar = Entity(parent=self, model='quad', origin=self.origin, z=-.01, color=color.red.tint(-.2), ignore=True)
        self.lines = Entity(parent=self.bar, origin=self.origin, y=-1, color=color.black33, ignore=True)
        self.text_entity.scale *= .7
        self.roundness = .25

        self.max_value = max_value
        self.clamp = True
        self.show_lines = show_lines
        self.show_text = show_text
        self.scale_x = self.scale_x # update rounded corners

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.scale_y = self.scale_y # update background's rounded corners
        self.value = self.max_value


    @property
    def value(self):
        return self._value


    @value.setter
    def value(self, n):
        if self.clamp:
            n = clamp(n, 0, self.max_value)

        self._value = n

        self.lines.enabled = False
        self.bar.animate_scale_x(n/self.max_value, duration=.1, curve=curve.in_out_bounce)
        invoke(setattr, self.lines, 'enabled', True, delay=.1)

        self.text_entity.text = f'{n} / {self.max_value}'

        if self.lines.enabled:
            self.lines.model = Grid(n, 1)

        if n / self.max_value >= self.scale_y / self.scale_x:
            aspect_ratio = n/self.max_value*self.scale_x / self.scale_y
            self.bar.model = Quad(radius=self.roundness, aspect=aspect_ratio)
        else:
            self.bar.model = 'quad'
        self.bar.origin = self.bar.origin



    def __setattr__(self, name, value):
        if name == 'show_text':
            self.text_entity.enabled = value

        if name == 'show_lines':
            self.lines.enabled = value
            return

        if name == 'bar_color':
            self.bar.color = value
            return


        super().__setattr__(name, value)

        if 'scale' in name and hasattr(self, 'roundness'):  # update rounded corners of background when scaling
            orginal_text_position = self.text_entity.position
            self.model = Quad(radius=self.roundness, aspect=self.world_scale_x / self.world_scale_y)
            self.origin = self.origin
            self.text_entity.position = orginal_text_position

        if 'scale' in name and hasattr(self, 'text_entity'):  # make sure the text doesn't scale awkwardly
            self.text_entity.world_scale_x = self.text_entity.world_scale_y


if __name__ == '__main__':
    app = Ursina()

    health_bar_1 = HealthBar(bar_color=color.lime.tint(-.25), roundness=.5, value=50)

    def input(key):
        if key == '+' or key == '+ hold':
            health_bar_1.value += 10
        if key == '-' or key == '- hold':
            health_bar_1.value -= 10

    app.run()
