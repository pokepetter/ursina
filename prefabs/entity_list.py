import sys
sys.path.append("..")
from pandaeditor import *
import os

class EntityList(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'scene_panel'
        self.parent = scene.ui.entity

        self.color = color.black33
        # self.is_editor = True


    def populate(self):
        print(len(scene.entities))
        self.y = .16 / 2

        y = 0
        for e in scene.entities:
            if not e.is_editor:
                print(e.name)
                # button = load_prefab('button')
                # button.is_editor = True
                # button.parent = self
                # button.position = (.161 , (-y * .031), 0)
                # button.scale = (.16, .03, 1)
                # button.color = color.gray
                # # button.text = e.name
                #
                # y += 1
