from ursina import *

from ursina.scripts.property_generator import generate_properties_for_class
@generate_properties_for_class()
class HealthBar(Button):

    def __init__(self, max_value=100, value=Default, roundness=.25, animation_duration=.1, show_text=True, show_lines=False, text_size=.7, origin=(-.5,.5), **kwargs):
        super().__init__(position=(-.45*window.aspect_ratio,.45), scale=(Text.size*20,Text.size), origin=origin,
        color=color.black66, highlight_color=color.black66, text='hp / max hp', text_size=text_size, radius=roundness, ignore=True)

        self.bar = Entity(parent=self, model=Quad(radius=roundness), origin=origin, z=-.005, color=color.red.tint(-.2), ignore=True)
        self.lines = Entity(parent=self.bar, y=-1, color=color.black33, ignore=True, enabled=show_lines, z=-.05)

        self.max_value = max_value
        self.clamp = True
        self.roundness = roundness
        self.animation_duration = animation_duration
        self.show_lines = show_lines
        self.show_text = show_text
        self.value = self.max_value if value == Default else value

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.text_entity.enabled = show_text


    def value_setter(self, n):
        if self.clamp:
            n = clamp(n, 0, self.max_value)

        self._value = n

        self.bar.animate_scale_x(n/self.max_value, duration=self.animation_duration, curve=curve.in_out_bounce)
        self.text_entity.text = f'{n} / {self.max_value}'

        if self.lines.enabled:
            self.lines.model = Grid(n, 1)
            self.lines.origin = (-.5,-.5)

        if n / self.max_value >= self.scale_y / self.scale_x:
            aspect_ratio = n/self.max_value*self.scale_x / self.scale_y
            self.bar.model = Quad(radius=self.roundness, aspect=aspect_ratio)
        else:
            self.bar.model = 'quad'
        self.bar.origin = self.bar.origin



    def show_text_getter(self):
        return self.text_entity.enabled
    def show_text_setter(self, value):
        self.text_entity.enabled = value

    def show_lines_getter(self):
        return self.lines.enabled
    def show_lines_setter(self, value):
        self.lines.enabled = value

    def bar_color_getter(self):
        return self.bar.color
    def bar_color_setter(self, value):
        self.bar.color = value



    def __setattr__(self, name, value):
        if 'scale' and hasattr(self, 'model') and self.model:  # update rounded corners of background when scaling
            self.model.aspect = self.world_scale_x / self.world_scale_y
            self.model.generate()
            if hasattr(self, 'text_entity') and self.text_entity:
                self.text_entity.world_scale = 25 * self.text_size

        super().__setattr__(name, value)


if __name__ == '__main__':
    app = Ursina()

    health_bar_1 = HealthBar(bar_color=color.lime.tint(-.25), roundness=.5, max_value=100, value=50)
    print(health_bar_1.text_entity.enabled, health_bar_1.text_entity.text)
    # health_bar_1.show_text = False
    # health_bar_1.show_lines = True

    def input(key):
        if key == '+' or key == '+ hold':
            health_bar_1.value += 10
        if key == '-' or key == '- hold':
            health_bar_1.value -= 10
            print('ow')
    app.run()
