import sys
from panda3d.core import NodePath


class Scene(NodePath):

    def __init__(self):
        super().__init__('')
        self.render = None
        self.world = None

        self.camera = None
        self.ui_camera = None
        self.canvas = None
        self.ui = None

        self.editor_camera_script = None
        self.editor = None
        self.editor_size = 1
        self.editor_font_size = 1

        self.entities = []
        self.entity = None # scene parent


    def set_up(self):
        from entity import Entity
        self.entity = Entity()
        self.entity.parent = self
        self.entity.name = 'untitled_scene'


    def new(self, discard_changes=False):
        if self.entity:
            destroy(self.entity)

        self.entity = Entity()
        self.entity.parent = self
        self.entity.name = 'untitled_scene'

        # if not discard_changes:
        #     if self.has_changes:
        #         # ask for save / discard
        #
        #         self.waiting_for_reply = True
        #
        # # ask for scene name
        #
        # if self.entity:
        #     destroy(self.entity)
        # scene.entity = Entity()
        # scene.entity.name = 'untitled_scene'
        # scene.editor.entity_list_header.text = scene.entity.name


sys.modules[__name__] = Scene()
