from pandaeditor import *

class LoadTextureButton():

    def __init__(self):
        self.path= None

    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            if self.path:
                entity = Entity()
                entity.name = self.path
                entity.model = loader.loadModel('models/quad.egg')
                entity.texture = self.path
                scene.editor_entities.append(entity)
                for e in scene.entities:
                    print(e.name)
