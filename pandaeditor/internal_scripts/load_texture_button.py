import sys
sys.path.append("..")
from pandaeditor import *

class LoadTextureButton():

    def __init__(self):
        self.path = None

    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            if self.path:
                self.load_sprite()

    @undoable
    def load_sprite(self):
        print('loaf')
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

        self.auto_created_canvas = True
        if not scene.canvas:
            scene.canvas = Canvas()
            self.auto_created_canvas = True

        entity.parent = scene.canvas
        scene.editor.entity_list.populate()

        # undo
        yield 'Load Sprite ' + entity.name
        destroy(entity)
        if self.auto_created_canvas:
            destroy(scene.canvas)
        scene.editor.entity_list.populate()
