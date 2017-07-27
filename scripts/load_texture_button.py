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
                entity.model = 'quad'
                entity.texture = self.path
                # print('x:', entity.texture.getOrigFileXSize(), 'y:', entity.texture.getOrigFileYSize())
                entity.scale = (entity.texture.getOrigFileXSize() / 100,
                                1,
                                entity.texture.getOrigFileYSize() / 100)
                entity.collision = True
                entity.add_script('button')
                scene.entities.append(entity)
                # print('entities:')
                # for e in scene.entities:
                #     if not e.is_editor:
                #         print(e.name, 'attached to ', e.parent.name)
