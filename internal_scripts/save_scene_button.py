import sys
sys.path.append("..")
from pandaeditor import *

class SaveScene():
    def __init__(self):
        self.t = 4
        self.enter_name = load_prefab('editor_button') # change to input field
        self.enter_name.parent = scene.editor
        self.enter_name.scale = (.25, .025)
        self.enter_name.color = color.black
        self.enter_name.text = 'save scene as...'
        self.enter_name.text_entity.align = 'left'
        self.enter_name.text_entity.x = -.45
        self.enter_name.enabled = False
        # self.enter_name.scripts.remove()


        self.text_field = load_prefab('editor_button') # change to input field
        self.text_field.parent = self.enter_name
        self.text_field.text = ''
        self.text_field.origin = (0, 1)

        self.save = load_prefab('editor_button')
        self.save.parent = self.enter_name
        self.save.text = 'save'
        self.save.origin = (0, 1)
        self.save.y = -1



    def input(self, key):
        if self.entity.hovered and key == 'left mouse down':
            if scene.entity.name == 'untitled_scene':
                print('show menu')
                self.enter_name.enabled = True
            save_prefab(scene.entity, 'scenes')

            for s in self.entity.scripts:
                print(s.__module__)

            self.enter_name.remove_script('editor_button')
            # print('saved scene:', 'scenes', scene_entity.name)
