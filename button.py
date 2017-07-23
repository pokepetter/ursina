from pandaeditor import *


class Button(object):

    def __init__(self):
        self.entity = None
        self.highlight_color = tuple(x + 0.2 for x in color.white)
        self.pressed_color = tuple(x - 0.2 for x in color.white)


    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'color':
            self.highlight_color = tuple(x + 0.1 for x in value)
            if color.to_hsv(self.color)[2] > 0.2:
                self.pressed_color = self.pressed_color = tuple(x - 0.2 for x in value)
            else:
                self.pressed_color = self.pressed_color = tuple(x + 0.2 for x in value)

    def input(self, key):
        if key == 'left mouse down':
            if self.entity.hovered:
                # print('click')
                self.entity.model.setColorScale(self.pressed_color)

        if key == 'left mouse up':
            if self.entity.hovered:
                self.entity.model.setColorScale(self.highlight_color)
            else:
                self.entity.model.setColorScale(self.color)

    def on_mouse_enter(self):
        self.entity.model.setColorScale(self.highlight_color)

    def on_mouse_exit(self):
        self.entity.model.setColorScale(self.color)
