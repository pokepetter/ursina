import sys
from panda3d.core import NodePath
from pandaeditor import color
# from pandaeditor.entity import Entity


class Scene(NodePath):

    def __init__(self):
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
        self.entity = None # scene parent

        self.has_changes = False




    def set_up(self):
        from pandaeditor.entity import Entity
        self.new(discard_changes=True)


    def new(self, discard_changes=False):
        if self.entity:
            destroy(self.entity)

        from pandaeditor.entity import Entity
        self.entity = Entity()
        self.entity.parent = render
        self.entity.name = 'untitled_scene'

        self.sky = Entity('sky')
        self.sky.parent = render
        print('_______', self.sky.parent)
        self.sky.scale *= 9999
        self.sky.model = 'sky_dome'
        self.sky.color = color.gray
        self.sky.texture = 'default_sky'

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
        # base.scene = Entity()
        # base.scene.name = 'untitled_scene'
        if self.editor:
            self.editor.hierarchy_panel_header.text = self.entity.name




sys.modules[__name__] = Scene()
