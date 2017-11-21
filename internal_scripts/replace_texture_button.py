import sys
sys.path.append("..")
from pandaeditor import *

class ReplaceTextureButton():

    def __init__(self):
        self.path = None

    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            if self.path:
                for s in scene.editor.selection:
                    try:
                        s.texture = os.path.basename(self.path)
                    except:
                        pass

                scene.editor.inspector.update_inspector()
