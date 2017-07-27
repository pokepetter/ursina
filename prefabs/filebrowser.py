import sys
sys.path.append("..")
from pandaeditor import *
import os

class Filebrowser(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'filebrowser'
        self.parent = scene.ui.entity
        # self.model = 'quad'
        self.color = color.black33
        self.file_types = None


    def populate(self, path):
        files = os.listdir(path)
        for i in range(math.floor(len(files) / 10) - 1):
            self.x -= 0.32 / 10
        self.z = .16 / 2

        z = 0
        x = 0
        for f in files:
            if self.file_types:
                for file_type in self.file_types:
                    if f.endswith(file_type) or file_type == '':
                        button = load_prefab('button')
                        button.is_editor = True
                        button.parent = self
                        button.position = (x * .161 , 0, (-z * .031))
                        button.scale = (.16, 1, .03)
                        button.color = color.gray
                        button.text = f
                        if path.endswith('textures'):
                            load_texture_button = button.add_script('load_texture_button')
                            load_texture_button.path = os.path.join('textures', f)

                        z += 1
                        if z >= 10:
                            z = 0
                            x += 1
                            # self.x -= .032


    def __setattr__(self, name, value):
        if name == 'path':
            self.populate(value)
        super().__setattr__(name, value)
