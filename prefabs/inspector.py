import sys
sys.path.append("..")
from pandaeditor import *
import os

class Inspector(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'inspector'
        self.parent = scene.ui
        self.is_editor = True
        self.model = 'quad'
        self.color = color.panda_button
        self.scale = (.15, .9)
        self.origin = (.5, .5)
        self.position = (.25, .2)

        # append self so update() runs
        self.scripts.append(self)

        self.button = load_prefab('editor_button')
        self.button.is_editor = True
        self.button.parent = self
        self.button.origin = (0, .25)
        self.button.x = -.5
        self.button.scale_y = .025
        self.button.color = color.gray
        self.button.text = 'transform'

        for j in range(3):
            for i in range(3):
                self.button = load_prefab('editor_button')
                self.button.is_editor = True
                self.button.parent = self
                self.button.origin = (-.5, .25)
                self.button.position = (-1 + (i / 3), -.025 - (j * .025))
                self.button.scale = (1 / 3, .025)
                self.button.color = color.gray
                self.button.text = str(i)

    def update(self, dt):
        # print('lol')
        # self.selected = editor.selection[0]
        if len(scene.editor.selection) > 0:
            self.visible = True
        else:
            self.visible = False


    #
    # def on_enable(self):
    #     print('enable')
    #     self.visible = True
    #
    # def on_disable(self):
    #     self.visible = False
