import sys
sys.path.append("..")
from pandaeditor import *

class ReplaceModelButton():

    def __init__(self):
        self.path = None

    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            if self.path:
                for s in scene.editor.selection:
                    try:
                        s.model.removeAllChildren()
                    except:
                        pass
                    if s.texture:
                        self.temp_texture = os.path.basename(s.texture.getFullpath())
                    s.model.removeNode()
                    s.model = os.path.basename(self.path).split('.')[0]
                    s.editor_collider = 'box'
                    if self.temp_texture:
                        s.texture = self.temp_texture

                scene.editor.inspector.update_inspector()
