from pandaeditor import *
from panda3d.core import TextNode


class Button(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'button'
        self.parent = scene.ui
        self.is_editor = False
        self.model = 'quad'
        if hasattr(self, 'model'):
            self.color = color.panda_button
        # self.texture = 'panda_button'

        self.collision = True
        self.collider = 'box'
        # self.text = ''
        self.text_entity = None


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
                self.text_entity.position = (0, 0, 0)
                self.text_entity.align = 'center'

            self.text_entity.text = value


    def __setattr__(self, name, value):

        if name == 'color':
            hsv = color.to_hsv(value)
            step = .2 if hsv[2] < .2 else -.2
            self.highlight_color = color.color(hsv[0], hsv[1], hsv[2] + step, clamp(hsv[3], .8, 1))
            self.pressed_color = color.color(hsv[0], hsv[1], hsv[2] - step, clamp(hsv[3], .8, 1))

        super().__setattr__(name, value)


    def input(self, key):
        if key == 'left mouse down':
            if self.hovered:
                self.model.setColorScale(self.pressed_color)
                try:
                    self.on_click()
                except:
                    pass

        if key == 'left mouse up':
            if self.hovered:
                self.model.setColorScale(self.highlight_color)
            else:
                self.model.setColorScale(self.color)


    def on_mouse_enter(self):
        self.model.setColorScale(self.highlight_color)

    def on_mouse_exit(self):
        self.model.setColorScale(self.color)


if __name__ == '__main__':
    app = PandaEditor()
    b = Button()
    app.run()
