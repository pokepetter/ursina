from pandaeditor import *

class EditorDraggable():

    def __init__(self):
        self.entity = None
    #     self.entity.collision = True
    #     self.entity.editor_collider = 'box'
    #
    #
    def on_mouse_enter(self):
        self.entity.model.setColorScale(self.highlight_color)

    def on_mouse_exit(self):
        self.entity.model.setColorScale(self.color)
