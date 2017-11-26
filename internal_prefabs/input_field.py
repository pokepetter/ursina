import sys
sys.path.append("..")
from pandaeditor import *
from panda3d.core import TextNode

class InputField(Entity):


    def __init__(self):
        super().__init__()
        self.name = 'input_field'
        self.parent = scene.ui
        self.model = 'quad'
        if self.model:
            self.color = color.panda_button

        self.collision = True
        self.collider = 'box'
        self.button_script = self.add_script('editor_button')
        self.button_script.color = color.panda_button

        self.add_script(InputFieldScript())
        self.text = 'text'

        print(self.scripts)


    def __setattr__(self, name, value):
        if name == 'color':
            try:
                self.button_script.color = value
            except:
                pass


        if name == 'text':
            if not self.text_entity:
                self.text_entity = load_prefab('text')
                self.text_entity.parent = scene
                self.text_entity.scale = (1,1,1)
                self.text_entity.rotation = (0,0,0)
                self.text_entity.is_editor = self.is_editor
                self.text_entity.wrtReparentTo(self.model)
                # self.text_entity.scale *= 2
                print('scale:', self.text_entity.scale)
                self.text_entity.position = (0, 0, 0)
                self.text_entity.text = value
                self.text_entity.align = 'left'
                self.text_entity.x = -1
                object.__setattr__(self, name, value)
            else:
                self.text_entity.text = value
                object.__setattr__(self, name, value)
        else:
            super().__setattr__(name, value)


class InputFieldScript():

    def __init__(self):
        self.editing = False

    def input(self, key):
        if key == 'left mouse down':
            if self.entity.hovered:
                print('focus')
                self.editing = True
            else:
                self.editing = False

        if self.editing and len(key) == 1:
            self.entity.text += key
            print(self.entity.text + key)

        if key == 'shift--':
            self.entity.text += '_'

        if key == 'space':
            self.entity.text += ' '

        if key == 'backspace':
            if len(self.entity.text) == 1:
                self.entity.text = ''
                return

            self.entity.text = self.entity.text[:-1]

        if key == 'enter':
            self.editing = False
