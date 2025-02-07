from ursina import Entity, Button, camera, color, Text, window, mouse, destroy
from ursina.scripts.grid_layout import grid_layout

class ButtonGroup(Entity):
    default_selected_color = color.azure

    def __init__(self, options, default='', min_selection=1, max_selection=1, origin=(-.5,.5,0), spacing=(0.025,0,0), **kwargs):
        super().__init__()
        self.deselected_color = Button.default_color
        self.selected_color = ButtonGroup.default_selected_color
        self.min_selection = min_selection
        self.max_selection = max(min_selection, max_selection)
        self.origin = origin
        self.spacing = spacing

        self.buttons = []
        self.selected = []
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
        [self.select(b) for b in self.buttons if b.value in value]


    def layout(self):
        [destroy(c) for c in self.buttons]
        self.buttons = []
        longest_word = max(self.options, key=len) + '__' # padding
        width = Text.get_width(longest_word) / Text.size / 2

        for e in self.options:
            b = Button(parent=self, text=e, name=e, scale_x=width, scale_y=.9, highlight_scale=1, pressed_scale=1)
            b.value = e
            self.buttons.append(b)

        grid_layout(self.buttons, origin=self.origin, spacing=self.spacing)


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
    from ursina import *
    app = Ursina()

    # Text.default_font = 'VeraMono.ttf'
    center = Entity(parent=camera.ui, model='circle', scale=.005, color=color.red, z=-1)
    gender_selection = ButtonGroup(('man', 'woman', 'other'), origin=(-.5,0))

    def on_value_changed():
        print('set gender:', gender_selection.value)
    gender_selection.on_value_changed = on_value_changed


    window.color = color._32

    # test
    for e in [(-.5,.5), (0,.5), (.5,.5), (-.5,0), (0,0), (.5,0), (-.5,-.5), (0,-.5), (.5,-.5)]:
        Button(
            text='*',
            model='quad',
            text_origin=e,
            scale=.095,
            origin=(-.5,.5),
            position = window.top_left + Vec2(*e)*.2 + Vec2(.1,-.1),
            tooltip=Tooltip(str(e)),
            on_click=Func(grid_layout, gender_selection.buttons, origin=e, spacing=gender_selection.spacing)
        )
    app.run()
