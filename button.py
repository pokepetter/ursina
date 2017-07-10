from pandaeditor import *

global screen_width
global screen_height
global aspect_ratio


class Button():

    def __init__(self):
        self.gameobject = None
        self.ui = None
        self.color = color.black


    def set_up(self):
        self.gameobject.collision = True
        # self.gameobject.model.showTightBounds()

        self.highlight_color = tuple(x + 0.1 for x in self.color)
        self.pressed_color = tuple(x - 0.2 for x in self.color)
        self.gameobject.model.setColorScale(self.color)


    def input(self, key):
        if key == 'left mouse down':
            if self.gameobject.hovered:
                print('click')
                self.gameobject.model.setColorScale(self.pressed_color)

        if key == 'left mouse up':
            if self.gameobject.hovered:
                self.gameobject.model.setColorScale(self.highlight_color)
            else:
                self.gameobject.model.setColorScale(self.color)

    def on_mouse_enter(self):
        print('enter')
        self.gameobject.model.setColorScale(self.highlight_color)

    def on_mouse_exit(self):
        print('exit')
        self.gameobject.model.setColorScale(self.color)
