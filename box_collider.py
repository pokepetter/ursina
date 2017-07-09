from panda3d.core import *

class BoxCollider():

    def __init__(self, size=(1,1,1)):
        self.center = (0,0,0)
        self.shape = CollisionBox(center, size[0], size[1], size[2])
        # collider_node_path = self.node_path.node.attachNewNode(CollisionNode('collider_node'))
        # collider_node_path.node().addSolid(shape)
