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
                # entity.is_editor = 1
                entity.name = self.path
                entity.model = 'quad'
                entity.texture = self.path
                # print('x:', entity.texture.getOrigFileXSize(), 'y:', entity.texture.getOrigFileYSize())
                entity.scale = (entity.texture.getOrigFileXSize() / 100,
                                entity.texture.getOrigFileYSize() / 100,
                                1)
                # print('random', random.uniform(-.1, .1))
                # entity.z += random.uniform(-.1, .1)
                entity.collision = True
                button_script = entity.add_script('editor_button')
                button_script.collider = None
                entity.editor_collider = 'box'
                scene.editor.entity_list.populate()
                # self.entity.parent.on_disable()
                # print('entities:')
                # for e in scene.entities:
                #     if not e.is_editor:
                #         print(e.name, 'attached to ', e.parent.name)
