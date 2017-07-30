import sys
sys.path.append("..")
from pandaeditor import *

class Button(Entity):


    def __init__(self):
        super().__init__()
        self.name = 'button'
        self.parent = scene.ui.entity
        self.model = 'quad'
        self.collision = True
        self.collider = 'box'
        self.button_script = self.add_script('button')
        self.button_script.color = color.gray
        self.text = ''

    def __setattr__(self, name, value):
        if name == 'color':
            try:
                self.button_script.color = value
            except:
                pass
        if name == 'position':
            value = (value[0] / 2, (value[1] / 2) - .1, value[2] / 2)

        if name == 'text':
            if len(value) > 0:
                t = load_prefab('text')
                t.is_editor = self.is_editor
                t.parent = self.model
                t.position = (0,-.1,0)
                t.scale = (.9,.9,.9)
                t.text = value
                # t.color = color.red


                object.__setattr__(self, name, t)

        else:
            super().__setattr__(name, value)
