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
        self.z = .16 / 2

        z = 0
        for e in scene.entities:
            if not e.is_editor:
                print(e.name)
                # button = load_prefab('button')
                # button.is_editor = True
                # button.parent = self
                # button.position = (.161 , 0, (-z * .031))
                # button.scale = (.16, 1, .03)
                # button.color = color.gray
                # # button.text = e.name
                #
                # z += 1
