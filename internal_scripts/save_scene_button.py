import sys
sys.path.append("..")
from pandaeditor import *

class SaveScene():
    def __init__(self):

        self.bg = load_prefab('panel')
        self.bg.parent = scene.editor
        # self.bg.model = 'quad'
        self.bg.scale = (.25, .025)
        self.bg.enabled = False

        self.enter_name = load_prefab('editor_button')
        self.enter_name.parent = self.bg
        self.enter_name.color = color.black
        self.enter_name.text = 'save scene as...'
        self.enter_name.text_entity.align = 'left'
        self.enter_name.text_entity.x = -.45
        self.enter_name.remove_script('editor_button')

        self.input_field = load_prefab('input_field') # change to input field
        self.input_field.is_editor = True
        self.input_field.parent = self.bg
        self.input_field.text_entity.x = -.45
        self.input_field.y = -1

        self.save = load_prefab('editor_button')
        self.save.parent = self.bg
        self.save.text = 'save'
        self.save.y = -2



    def input(self, key):
        if self.entity.hovered and key == 'left mouse down' or key == 'control-s':
            if scene.entity.name == 'untitled_scene':
                print('show menu')
                self.bg.enabled = True
            else:
                save_prefab(scene.entity, 'scenes')

                for s in self.entity.scripts:
                    print(s.__module__)


                # print('saved scene:', 'scenes', scene_entity.name)
