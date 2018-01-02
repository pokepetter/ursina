import sys
sys.path.append("..")
from pandaeditor import *

class LoadModelButton():

    def __init__(self):
        self.path = None

    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            if self.path:
                print(self.path)
                self.load_model()

    @undoable
    def load_model(self):
        entity = Entity()
        entity.name = os.path.basename(self.path).split('.')[0]
        entity.model = os.path.basename(self.path).split('.')[0]

        entity.collision = True
        entity.editor_collider = 'box'
        button_script = entity.add_script('editor_draggable')
        scene.editor.entity_list.populate()

        # undo
        yield 'Load Model ' + entity.name
        destroy(entity)
        scene.editor.entity_list.populate()
