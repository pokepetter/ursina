import sys
sys.path.append("..")
from pandaeditor import *
import os

class EntityList(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'scene_panel'
        self.parent = scene.ui

        self.color = color.black33
        self.t = 0
        self.buttons = list()

        self.max_vertical = 10
        self.button_size = (.16, .02)

        self.origin = (-.5, .5)
        self.position = (-.25, .2)
        # self.scale = (.5, .5)

        self.temp_entity_list = list()
        self.scripts.append(self)
        scene.entities.append(self)


    def update(self, dt):
        self.t += 1
        if self.t >= 50:
            if scene.entities != self.temp_entity_list:
                self.populate()
            self.t = 0


    def populate(self):
        self.temp_entity_list = list(scene.entities)

        for b in self.buttons:
            destroy(b)
        self.buttons.clear()

        y = 0
        x = 0
        for e in self.temp_entity_list:
            if not e.is_editor:
                button = load_prefab('button')
                button.is_editor = True
                button.parent = self
                button.origin = (-.5, .5)
                button.position = (
                    x * (self.button_size[0]),
                    (-y * (self.button_size[1])))
                button.scale = self.button_size
                button.color = color.black66
                button.text = e.name
                # button.text_entity.size = .5
                # menu_toggler = button.add_script('menu_toggler')
                # menu_toggler.target = self
                self.buttons.append(button)

                y += 1
                if y >= self.max_vertical:
                    y = 0
                    x += 1

        # self.close_button = load_prefab('button')
        # self.close_button.is_editor = True
        # self.close_button.parent = self
        # self.close_button.origin = (.5, -.5)
        # self.close_button.position = ((x) * self.button_size[0] , 0)
        # self.close_button.scale = (self.button_size[1], self.button_size[1])
        # self.close_button.color = color.red
        # self.close_button.text = 'x'
        # self.close_button.text_entity.x = 0
