from pandaeditor import *

class ReplaceTextureButton():

    def __init__(self):
        self.path = None

    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            if self.path:
                self.replace_texture()

    @undoable
    def replace_texture(self):
        self.target_entities = list()
        self.original_textures = list()
        for s in scene.editor.selection:
            self.original_textures.append(str(s.texture.getFullpath()))
            self.target_entities.append(s)

        for s in scene.editor.selection:
            s.texture = self.path

        scene.editor.inspector.update_inspector()

        # undo
        yield 'replace texture'
        print('--------------', self.original_textures)
        for i in range(len(self.target_entities)):
            self.target_entities[i].texture = self.original_textures[i]
        scene.editor.inspector.update_inspector()
