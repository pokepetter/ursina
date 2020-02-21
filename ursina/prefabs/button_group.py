from ursina import *


class ButtonGroup(Entity):
    def __init__(self, options=None, **kwargs):
        super().__init__()
        self.deselected_color = Button.color
        self.selected_color = color.orange
        self.max_selection = 1

        self.buttons = list()
        self.selected = list()
        self.options = options

        self.label = Text(parent=self, scale=1/.04*.9, origin=(-.5, -.35))
        self.parent = camera.ui
        self.scale = Text.size * 2

        for key, value in kwargs.items():
            setattr(self, key, value)


    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        self._options = value
        self.layout()


    @property
    def value(self):
        return


    @property
    def title(self):
        return self.label.text

    @title.setter
    def title(self, value):
        self.label.text = value


    def layout(self):
        [destroy(c) for c in self.buttons]
        self.buttons = list()
        spacing = .05
        longest_word = max(self.options, key=len) + '__' # padding
        width = Text.get_width(longest_word) / Text.size / 2

        for e in self.options:
            b = Button(parent=self, text=e, name=e, scale_x=width, scale_y=.9)
            b.value = e
            b.highlight_scale = 1
            b.highlight_color = color.orange
            b.pressed_scale = 1
            self.buttons.append(b)

        grid_layout(self.buttons, spacing=(0.025,0,0), origin=(-.5, .5, 0))
        for b in self.buttons:
            b.x += width / 2


    def input(self, key):
        if key == 'left mouse down' and mouse.hovered_entity in self.buttons:
            b = mouse.hovered_entity

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



if __name__ == '__main__':
    app = Ursina()

    Text.default_font = 'VeraMono.ttf'
    button_group = ButtonGroup(('man', 'woman', 'other'))

    app.run()
