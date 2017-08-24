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


    def populate(self):
        for b in self.buttons:
            destroy(b)



        self.close_button = load_prefab('button')
        self.close_button.is_editor = True
        self.close_button.parent = self
        self.close_button.position = (.161 , .031, 0)
        self.close_button.scale = (.003, .003, 1)
        self.close_button.color = color.red

        for i in range(math.floor(len(self.files) / 10) - 1):
            self.x -= 0.32 / 10
        self.y = .16 / 2


        y = 0
        x = 0
        for f in self.files:
            print(f)
            if self.file_types:
                for file_type in self.file_types:
                    if f.endswith(file_type) or file_type == '':
                        button = load_prefab('button')
                        button.is_editor = True
                        button.parent = self
                        button.position = (x * .161 , (-y * .031), 0)
                        button.scale = (.3, .03, 1)
                        button.color = color.gray
                        # button.text = f
                        self.buttons.append(button)
                        if self.path.endswith('textures'):
                            load_texture_button = button.add_script('load_texture_button')
                            load_texture_button.path = os.path.join('textures', f)

                        y += 1
                        if y >= 10:
                            y = 0
                            x += 1
                            # self.x -= .032

    def on_enable(self):
        print('enable')
        self.visible = True
        self.old_files = self.files
        self.files = os.listdir(self.path)
        if self.files != self.old_files:
            self.populate()


    def on_disable(self):
        self.visible = False

# test
# i = Filebrowser()
# i.path = "E:/UnityProjects/pandaeditor/textures"
# i.populate()
