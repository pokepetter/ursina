from pandaeditor import *

class Voxel(Entity):

    def __init__(self):
        super().__init__()
        self.model = 'cube'
        self.collider = 'box'
        self.texture = 'white_cube'
        self.scripts.append(self)

    def input(self, key):
        if key == 'left mouse down' and self.hovered:
            if keys.alt:
                destroy(self)
            else:
                voxel = load_prefab('voxel')
                voxel.parent = self.parent
                voxel.position = self.position + mouse.normal
