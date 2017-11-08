import sys
sys.path.append("..")
from pandaeditor import *
from panda3d.core import TextNode

class EditorButton(Entity):


    def __init__(self):
        super().__init__()
        self.name = 'editor_button'
        self.parent = scene.ui
        self.is_editor = True
        self.model = 'quad'
        if self.model:
            self.color = color.panda_button
        # self.texture = 'panda_button'

        self.collision = True
        self.collider = 'box'
        self.button_script = self.add_script('editor_button')
        self.button_script.color = color.panda_button
        self.text = ''
        self.text_entity = None


    def __setattr__(self, name, value):
        if name == 'color':
            try:
                self.button_script.color = value
            except:
                pass


        if name == 'text':
            if len(value) > 0:
                if not self.text_entity:
                    self.text_entity = load_prefab('text')
                    self.text_entity.parent = scene.render
                    self.text_entity.is_editor = self.is_editor
                    self.text_entity.wrtReparentTo(self.model)
                    self.text_entity.position = (0, 0, 0)
                    self.text_entity.text = value
        else:
            super().__setattr__(name, value)
