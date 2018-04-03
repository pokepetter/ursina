from pandaeditor import *
from panda3d.core import TextNode


class Button(Entity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
                self.text_entity.position = (0, 0, 0)
                self.text_entity.align = 'center'

            self.text_entity.text = value


    def __setattr__(self, name, value):

        if name == 'color':
            hsv = color.to_hsv(value)
            step = .2 if hsv[2] < .2 else -.2
            self.highlight_color = color.color(hsv[0], hsv[1], hsv[2] + step, clamp(hsv[3], .8, 1))
            self.pressed_color = color.color(hsv[0], hsv[1], hsv[2] - step, clamp(hsv[3], .8, 1))

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
                self.model.setColorScale(self.pressed_color)

        if key == 'left mouse up':
            if self.hovered:
                self.model.setColorScale(self.highlight_color)
            else:
                self.model.setColorScale(self.color)


    def on_mouse_enter(self):
        self.model.setColorScale(self.highlight_color)
        if hasattr(self, 'tooltip'):
            # self.tooltip.scale = (0,0,0)
            self.tooltip.enabled = True
            # self.tooltip_scaler = self.tooltip.animate_scale(self.tooltip.target_scale)

    def on_mouse_exit(self):
        self.model.setColorScale(self.color)
        self.tooltip.enabled = False



if __name__ == '__main__':
    app = PandaEditor()
    b = Button()
    b.tooltip = Tooltip()
    b.scale *= .5
    b.color = color.azure
    b.origin = (-.5, -.5)
    app.run()
