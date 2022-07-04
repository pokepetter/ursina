from ursina import Entity, Button, camera, color, Text, window, mouse
from ursina.scripts.grid_layout import grid_layout

class ButtonGroup(Entity):
    def __init__(self, options=None, default='', min_selection=1, max_selection=1, **kwargs):
        super().__init__()
        self.deselected_color = Button.color
        self.selected_color = color.azure
        self.min_selection = min_selection
        self.max_selection = max(min_selection, max_selection)

        self.buttons = list()
        self.selected = list()
        self.options = options

        self.parent = camera.ui
        self.scale = Text.size * 2

        for key, value in kwargs.items():
            setattr(self, key, value)

        if default:
            for b in [e for e in self.buttons if e.value == default]:
                self.select(b)
        else:
            for i in range(min_selection):
                self.select(self.buttons[i])


    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        self._options = value
        self.layout()


    @property
    def value(self):
        if self.max_selection == 1:
            return self.selected[0].value

        return [b.value for b in self.selected]

    @value.setter
    def value(self, value):
        print('set buttongroup value to:', value)
        [self.select(b) for b in self.buttons if b.value in value]



    def layout(self):
        [destroy(c) for c in self.buttons]
        self.buttons = []
        spacing = .05
        longest_word = max(self.options, key=len) + '__' # padding
        width = Text.get_width(longest_word) / Text.size / 2

        for e in self.options:
            b = Button(parent=self, text=e, name=e, scale_x=width, scale_y=.9)
            b.value = e
            b.highlight_scale = 1
            b.pressed_scale = 1
            self.buttons.append(b)

        grid_layout(self.buttons, spacing=(0.025,0,0), origin=(-.5, .5, 0))


    def input(self, key):
        if key == 'left mouse down' and mouse.hovered_entity in self.buttons:
            self.select(mouse.hovered_entity)


    def select(self, b):
        if b in self.selected and self.min_selection > 0 and len(self.selected) >= self.min_selection:
            return

        # add
        if not b in self.selected:
            b.color = self.selected_color
            self.selected.append(b)

            if len(self.selected) > self.max_selection:
                # remove oldest addition
                self.selected[0].color = self.deselected_color
                self.selected.pop(0)
        # remove
        else:
            b.color = self.deselected_color
            self.selected.remove(b)

        self.on_value_changed()



    def on_value_changed(self):
        pass



if __name__ == '__main__':
    from ursina import Ursina
    app = Ursina()

    # Text.default_font = 'VeraMono.ttf'
    gender_selection = ButtonGroup(('man', 'woman', 'other'))
    on_off_switch = ButtonGroup(('off', 'on'), min_selection=1, y=-.1, default='on', selected_color=color.red)

    def on_value_changed():
        print('set gender:', gender_selection.value)
    gender_selection.on_value_changed = on_value_changed

    def on_value_changed():
        print('turn:', on_off_switch.value)
    on_off_switch.on_value_changed = on_value_changed

    window.color = color._32
    app.run()
