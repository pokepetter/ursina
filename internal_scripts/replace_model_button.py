import sys
sys.path.append("..")
from pandaeditor import *

class ReplaceModelButton():

    def __init__(self):
        self.path = None

    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            if self.path:
                self.replace_models()

    @undoable
    def replace_models(self):
        original_models = list()
        target_entities = list()
        for s in scene.editor.selection:
            original_models.append(s.model)
            target_entities.append(s)

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

        yield 'replace model'
        for i in len(target_entities):
            # scene.editor.selections[i].model = original_models[i]
            # s.editor_collider = 'box'

            s = target_entities[i]

            try:
                s.model.removeAllChildren()
            except:
                pass
            if s.texture:
                self.temp_texture = os.path.basename(s.texture.getFullpath())
            s.model.removeNode()
            s.model = original_models[i]
            s.editor_collider = 'box'
            if self.temp_texture:
                s.texture = self.temp_texture
        scene.editor.inspector.update_inspector()
