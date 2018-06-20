from ursina import *
from panda3d.core import TextNode

class EditorButton(Button):

    def __init__(self):
        super().__init__()
        self.name = 'editor_draggable'
        self.is_editor = True
