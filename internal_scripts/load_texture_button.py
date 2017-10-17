import sys
sys.path.append("..")
from pandaeditor import *

class LoadTextureButton():

    def __init__(self):
        self.path = None

    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            if self.path:
                entity = Entity()
                entity.name = os.path.basename(self.path)
                entity.model = 'quad'
                entity.texture = self.path
                entity.scale = (entity.texture.getOrigFileXSize() / 1000,
                                entity.texture.getOrigFileYSize() / 1000,
                                1)
                entity.collision = True
                button_script = entity.add_script('editor_button')
                button_script.collider = None
                entity.editor_collider = 'box'
                scene.editor.entity_list.populate()

                if scene.editor.ui_canvas:
                    entity.parent = scene.editor.ui_canvas
