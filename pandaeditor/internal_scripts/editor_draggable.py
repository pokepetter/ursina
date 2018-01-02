from pandaeditor import *

class EditorDraggable():

    def __init__(self):
        self.entity = None
        self.hover_color = color.color(0, 0, .9)
        self.click_color = color.color(190, .5, .9, .8)


    def input(self, key):
        if self.entity.hovered:
            if key == 'left mouse down':
                self.entity.color = self.click_color
            elif key == 'left mouse up':
                self.entity.color = self.hover_color


    def on_mouse_enter(self):
        self.original_color = self.entity.color
        self.entity.color = self.hover_color


    def on_mouse_exit(self):
        self.entity.color = self.original_color


if __name__ == '__main__':
    app = PandaEditor()
    e = Entity("test entity")
    e.model = 'quad'
    e.collision = True
    e.collider = 'box'
    e.add_script(EditorDraggable())
    app.run()
