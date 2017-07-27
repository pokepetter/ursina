import sys


class Scene(object):

    def __init__(self):
        self.app = None
        self.render = None
        self.camera = None
        self.asset_folder = None
        self.editor_camera = None
        self.ui = None
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

sys.modules[__name__] = Scene()
