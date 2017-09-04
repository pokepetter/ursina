import sys
from panda3d.core import NodePath


class Scene(NodePath):

    def __init__(self):
        super().__init__('')
        self.app = None
        self.base = None
        self.render = None
        self.world = None

        self.camera = None
        self.ui_camera = None
        self.ui = None

        self.asset_folder = None
        self.editor_camera_script = None
        self.editor = None
        self.entities = []

    def clear(self):
        print('clearing scene')
        for e in self.entities:
            try: e.model.removeNode()
            except: pass
            try: e.removeNode()
            except: pass
            del e

        self.entities = []
        print('entities', self.entities)


    def save(self, name):
        for e in self.entities:
            if not e.is_editor:
                # s = 'self.entity = Entity()'
                # s += 'self.entity.name = ' e.name
                # s += 'self.entity.parent = ' + str(e.parent)
                # s += 'self.entity.position' + str(e.position)
                print(inspect.getmembers(e))
                # for s in e.scripts:



                # print(s)


sys.modules[__name__] = Scene()
