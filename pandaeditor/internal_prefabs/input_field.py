import sys
sys.path.append("..")
from pandaeditor import *
from panda3d.core import TextNode

class InputField(Button):

    def __init__(self):
        super().__init__()
        self.name = 'input_field'
        # self.parent = scene.editor
        self.is_editor = True

        self.editing = False
        self.text = '...'
        self.text_entity.scale *= 5
        self.text_entity.position = (-.45, .45)
        self.text_entity.align = 'left'



    def input(self, key):
        if key == 'left mouse down':
            if self.hovered:
                self.editing = True
                if self.text == '...':
                    self.text = ''
            else:
                self.editing = False

        if not self.editing:
            return

        if len(key) == 1:
            self.text += key

        if key == 'shift--':
            self.text += '_'

        if key == 'space':
            self.text += ' '

        if key == 'backspace':
            if len(self.text) == 1:
                self.text = ''
                return

            self.text = self.text[:-1]

        if key == 'enter':
            if held_keys['shift']:
                self.editing = False
            else:
                self.text += '\n'

if __name__ == '__main__':
    app = PandaEditor()
    window.size = (window.size[0] * .5, window.size[1] * .5)
    test = InputField()
    # test.
    app.run()
