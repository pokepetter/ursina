import sys
sys.path.append("..")
from pandaeditor import *

class VoxelTool(Entity):

    def __init__(self):
        super().__init__()
        self.scripts.append(self)

        for z in range(10):
            for x in range(10):
                voxel = load_prefab('voxel', True)
                voxel.position = (x, 0, z)
        # print('c', self.children)

    # def input(self, key):
    #     print(key)

    # def update(self, dt):
    #     print(keys.alt)
