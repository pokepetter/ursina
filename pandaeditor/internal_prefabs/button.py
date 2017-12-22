import sys
sys.path.append("..")
from pandaeditor import *
from panda3d.core import TextNode

class Button(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'button'
        self.parent = scene.ui
        self.is_editor = False
        self.model = 'quad'
        if self.model:
            self.color = color.panda_button
        # self.texture = 'panda_button'

        self.collision = True
        self.collider = 'box'
        self.text = ''
        self.text_entity = None
        self.highlight_color = tuple(x + 0.2 for x in color.white)
        self.pressed_color = tuple(x - 0.2 for x in color.white)


    def __setattr__(self, name, value):
        if name == 'color':
            self.highlight_color = tuple(x + 0.2 for x in value)
            self.pressed_color = tuple(
                x - 0.2 if value[2] > 0.2
                else x + .2
                for x in value
                )

        if name == 'text':
            if len(value) > 0:
                if not self.text_entity:
                    self.text_entity = load_prefab('text')
                    self.text_entity.parent = scene.render
                    self.text_entity.is_editor = self.is_editor
                    self.text_entity.wrtReparentTo(self.model)
                    self.text_entity.position = (0, 0, 0)
                    self.text_entity.text = value
                    self.text_entity.align = 'center'
                    object.__setattr__(self, name, value)
                else:
                    self.text_entity.text = value
        else:
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

    def on_mouse_exit(self):
        self.model.setColorScale(self.color)
