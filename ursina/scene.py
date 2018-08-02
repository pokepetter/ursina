import sys
from panda3d.core import NodePath
from ursina import color
# from ursina.ursinastuff import destroy
# from ursina.entity import Entity


class Scene(NodePath):

    def __init__(self):
        super().__init__('scene')
        self.render = None
        self.world = None

        self.camera = None
        self.ui_camera = None
        self.canvas = None
        self.ui = None

        self.editor = None
        self.editor_size = 1
        self.editor_font_size = 1

        self.entities = []
        self.hidden = NodePath('hidden')

        self.has_changes = False


    def set_up(self):
        from ursina.entity import Entity
        self.reparent_to(render)


    def clear(self):
        self.to_keep = list()
        self.to_destroy = list()
        for e in self.entities:
            if hasattr(e, 'eternal') and e.eternal:
                self.to_keep.append(e)
            else:
                self.to_destroy.append(e)
                print('dest:', e)

        for d in self.to_destroy:
            print('destroy', e)
            self.entities.remove(d)
            d.remove_node()

        self.entities = self.to_keep



sys.modules[__name__] = Scene()
