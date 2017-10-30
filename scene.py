import sys
from panda3d.core import NodePath


class Scene(NodePath):

    def __init__(self):
        super().__init__('')
        self.render = None
        self.world = None

        self.camera = None
        self.ui_camera = None
        self.ui = None

        self.editor_camera_script = None
        self.editor = None

        self.entities = []
        self.entity = None # scene parent


    def set_up(self):
        from entity import Entity
        self.entity = Entity()
        self.entity.parent = self
        self.entity.name = 'untitled_scene'


    def new(self):
        # from entity import Entity
        if self.entity:
            destroy(self.entity)

        self.entity = Entity()
        self.entity.parent = self
        self.entity.name = 'untitled_scene'


sys.modules[__name__] = Scene()
