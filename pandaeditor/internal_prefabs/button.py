from pandaeditor import *
from panda3d.core import TextNode


class Button(Entity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'button'
        self.parent = scene.ui
        self.is_editor = False
        self.model = 'quad'
        self.color = color.panda_button
        # self.texture = 'panda_button'

        self.collision = True
        self.collider = 'box'
        # self.text = 'button'
        self.text_entity = None

        for key, value in kwargs.items():
            setattr(self, key, value)


    @property
    def text(self):
        if self.text_entity:
            return self.text_entity.text

    @text.setter
    def text(self, value):
        if type(value) is str:
            if not self.text_entity:
                self.text_entity = Text()
                self.text_entity.parent = render
                self.text_entity.is_editor = self.is_editor
                self.text_entity.wrtReparentTo(self.model)
                self.text_entity.position = (0, 0, -.1)
                self.text_entity.scale *= 2

            self.text_entity.text = value
            self.text_entity.align = 'center'


    def __setattr__(self, name, value):
        if name == 'color':
            # ignore setting original color if the button is modifying its own color on enter, exit or click
            if ('self' in inspect.currentframe().f_back.f_locals
            and inspect.currentframe().f_back.f_locals['self'] != self
            or inspect.stack()[1][3] == '__init__'):
                self.original_color = value
                self.highlight_color = color.tint(self.original_color, .2)
                self.pressed_color = color.tint(self.original_color, -.2)


        if name == 'origin':
            super().__setattr__(name, value)
            try:    # update collider position by making a new one
                self.collider.remove()
                self.collider = 'box'
            except:
                pass

        super().__setattr__(name, value)


    def input(self, key):
        if key == 'left mouse down':
            if self.hovered:
                self.color = self.pressed_color

        if key == 'left mouse up':
            if self.hovered:
                self.color = self.highlight_color


    def on_mouse_enter(self):
        self.color = self.highlight_color

        if hasattr(self, 'tooltip'):
            self.tooltip_scale = self.tooltip.scale
            self.tooltip.scale = (0,0,0)
            self.tooltip.enabled = True
            self.tooltip_scaler = self.tooltip.animate_scale(self.tooltip_scale)


    def on_mouse_exit(self):
        self.color = self.original_color

        if hasattr(self, 'tooltip'):
            if hasattr(self, 'tooltip_scaler'):
                self.tooltip_scaler.finish()
            self.tooltip.enabled = False


class Test():
    def __init__(self):
        self.b = Button(color = color.red)
        self.b.scale *= .5
        self.b.color = color.azure
        self.b.origin = (-.5, -.5)
        self.b.text = 'text'
        self.b.text_entity.scale *= 2

if __name__ == '__main__':
    app = PandaEditor()
    t = Test()
    t.b.tooltip = Tooltip()
    app.run()
