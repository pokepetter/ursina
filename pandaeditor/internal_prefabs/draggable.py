from pandaeditor import *

class Draggable(Button):

    # drag_mode = False
    # label = Text('drag mode', enabled=False, scale=(.25, .25))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Draggable.label.parent = camera.ui
        # Draggable.label.enabled = Draggable.drag_mode
        # Draggable.label.scale *= .1
        # Draggable.label.position = (-.5 * window.aspect_ratio, .48)
        self.require_key = None
        self.dragging = False


    def input(self, key):
        super().input(key)
        # if key == 'tab':
        #     Draggable.drag_mode = not Draggable.drag_mode
        #     Draggable.label.enabled = not Draggable.label.enabled

        if self.hovered and key == 'left mouse down':
            if not self.require_key or held_keys[self.require_key]:
                self.dragging = True

        if key == 'left mouse up':
            self.dragging = False

    def update(self, dt):
        if self.dragging:
            self.x += mouse.velocity[0] * camera.fov
            self.y += mouse.velocity[1] * camera.fov



if __name__ == '__main__':
    app = PandaEditor()
    camera.orthographic = True

    e = Draggable()
    e.parent = scene
    e.require_key = 'shift'
    app.run()
