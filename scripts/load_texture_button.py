import sys
sys.path.append("..")
from pandaeditor import *

class LoadTextureButton():

    def __init__(self):
        self.path= None

    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            if self.path:
                entity = Entity()
                # entity.is_editor = True
                entity.name = self.path
                entity.model = loader.loadModel('models/cube.egg')
                # entity.model.setHpr((0,180,0))
                entity.texture = self.path
                scene.entities.append(entity)
                print('entities:')
                for e in scene.entities:
                    if not e.is_editor:
                        print(e.name, e.parent.name)
