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
            if (e.has_ancestor(self.editor)
            or e is self.camera
            or e is self.editor
            or e is self.ui
            or e is self.editor.grid):
                pass
            else:
                # print(e)
                try: e.model.removeNode()
                except: pass
                try: e.removeNode()
                except: pass
                del e

                self.entities.remove(e)
        print('entities', self.entities)





sys.modules[__name__] = Scene()
