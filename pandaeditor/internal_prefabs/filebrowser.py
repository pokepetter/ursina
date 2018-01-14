import sys
sys.path.append("..")
from pandaeditor import *
import os

class Filebrowser(Entity):

    def __init__(self):
        super().__init__()
        self.enabled = False
        self.name = 'filebrowser'
        self.parent = camera.ui
        self.is_editor = True

        self.color = color.black33

        self.path = ''
        self.file_types = None
        self.buttons = list()
        self.files = None

        self.max_vertical = 10
        self.button_size = (.16, .025)
        self.button_type = ''

        self.close_button = EditorButton()
        self.close_button.name = 'close_button'
        self.close_button.parent = self
        self.close_button.position = (0, 0, 10)
        self.close_button.scale *= 10
        self.close_button.color = color.black33
        self.close_button.highlight_color = self.close_button.color
        menu_toggler = self.close_button.add_script('menu_toggler')
        menu_toggler.target = self


    def populate(self):
        print('populate')
        self.close_button.enabled = True
        for b in self.buttons:
            destroy(b)


        y = 0
        x = 0
        if self.files:
            for f in self.files:
                if f.startswith('__'):
                    continue

                for file_type in self.file_types:
                    if f.endswith(file_type) or file_type == '':
                        print('file:', f)
                        button = EditorButton()
                        button.is_editor = True
                        button.parent = self
                        button.origin = (-.5, .5)
                        button.position = (
                            x * (self.button_size[0] + .001),
                            (-y * (self.button_size[1] + .001)))
                        button.scale = self.button_size
                        button.color = color.panda_button
                        menu_toggler = button.add_script('menu_toggler')
                        menu_toggler.target = self
                        button.text = os.path.basename(f).split('.')[0]
                        button.text_entity.position = (-.45, 0)
                        button.text_entity.align = 'left'
                        self.buttons.append(button)
                        try:
                            self.load_button = button.add_script(self.button_type)
                            self.load_button.path = button.text
                        except:
                            print('no script:', self.button_type)
                        # print('path', self.load_button.path)

                        y += 1
                        if y > self.max_vertical:
                            y = 0
                            x += 1

        # special case for script browser, add 'new script' button
        if self.button_type == 'add_script_button':
            button = EditorButton()
            button.is_editor = True
            button.parent = self
            button.origin = (-.5, .5)
            button.position = (
                x * (self.button_size[0]),
                (-y * (self.button_size[1])))
            button.scale = self.button_size
            button.color = color.panda_button
            menu_toggler = button.add_script('menu_toggler')
            menu_toggler.target = self
            button.text = f
            button.text_entity.position = (-.45, 0)
            button.text_entity.origin = (-.5, 0)
            self.buttons.append(button)
            self.load_button = button.add_script('new_script_button')
            x += 1

        if self.button_type == 'load_scene_button':
            button = EditorButton()
            button.parent = self
            button.origin = (-.5, .5)
            button.position = (
                x * (self.button_size[0]),
                (-y * (self.button_size[1])))
            button.scale = self.button_size
            menu_toggler = button.add_script('menu_toggler')
            menu_toggler.target = self
            button.text = '[new scene]'
            button.text_entity.align = 'left'
            button.text_entity.position = (-.45, 0)
            button.text_entity.origin = (-.5, 0)
            self.buttons.append(button)
            button.add_script('new_scene')
            x += 1

        self.x = - ((x + 1) * self.button_size[0]) / 2.0
        self.y = ((y) * self.button_size[1]) / 2




    def on_enable(self):
        # print('filebrowser enable:', (self.path))
        self.x = 0
        self.old_files = self.files
        try:
            self.files = os.listdir(self.path)
            print('file count:', len(self.files))
        except:
            print('0 files in directory')
            print(self.file_types, self.button_type)

        self.populate()


    def on_disable(self):
        self.x = 100

if __name__ == '__main__':
    app = PandaEditor()
    test = Filebrowser()
    test.path = application.internal_texture_folder
    test.file_types = (('.jpg'))
    test.button_type = 'load_sprite_button'
    app.run()
