from ursina import *


class SelectTool(Entity):
    def __init__(self, parent, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.name = 'select tool'
        self.description = 'SelectTool'
        self.hotkeys = ['q', ]

    def input(self, key):
        if key == 'left mouse down':
            if not mouse.hovered_entity:
                self.parent.selection = []
            elif not held_keys['control']:
                self.parent.selection = [mouse.hovered_entity, ]
            else:
                self.parent.selection.append(mouse.hovered_entity)
