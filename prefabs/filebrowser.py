import sys
sys.path.append("..")
from pandaeditor import *
import os

class Filebrowser(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'filebrowser'
        self.parent = scene.ui
        self.color = color.black33

        self.path = ''
        self.buttons = list()
        self.file_types = None
        self.files = None

        self.max_vertical = 10
        self.button_size = (.15, .03)


    def populate(self):
        for b in self.buttons:
            destroy(b)

        y = 0
        x = 0
        for f in self.files:
            if self.file_types:
                for file_type in self.file_types:
                    if f.endswith(file_type) or file_type == '':
                        button = load_prefab('button')
                        button.is_editor = True
                        button.parent = self
                        button.origin = (-.5, .5)
                        button.position = (
                            x * (self.button_size[0]),
                            (-y * (self.button_size[1])))
                        button.scale = self.button_size
                        button.color = color.black66
                        menu_toggler = button.add_script('menu_toggler')
                        menu_toggler.target = self
                        button.text = f
                        self.buttons.append(button)
                        if self.path.endswith('textures'):
                            self.load_texture_button = button.add_script('load_texture_button')
                            self.load_texture_button.path = os.path.join('textures', f)


                        y += 1
                        if y >= self.max_vertical:
                            y = 0
                            x += 1

        self.x = - ((x) * self.button_size[0] / 4)

        self.close_button = load_prefab('button')
        self.close_button.is_editor = True
        self.close_button.parent = self
        self.close_button.origin = (.5, -.5)
        self.close_button.position = ((x) * self.button_size[0] , 0)
        self.close_button.scale = (self.button_size[1], self.button_size[1])
        self.close_button.color = color.red
        self.close_button.text = 'x'
        menu_toggler = self.close_button.add_script('menu_toggler')
        menu_toggler.target = self


    def on_enable(self):
        print('enable')
        self.visible = True
        self.old_files = self.files
        self.files = os.listdir(self.path)
        if self.files != self.old_files:
            self.populate()


    def on_disable(self):
        self.visible = False
