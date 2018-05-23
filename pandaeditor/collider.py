from panda3d.core import CollisionNode, CollisionBox
from panda3d.core import NodePath
from panda3d.core import Vec3


class Collider(NodePath):
    def __init__(self):
        super().__init__('collider_node_path')
        self.entity = None
        self.node_path = None


    def make_collider(self):
        pos = (0,0,0)
        if hasattr(self.entity, 'model') and self.entity.model != None:
            start, end = self.entity.model.getTightBounds()
            size = (end - start) / 2
            y = max(.01, size[1])
            z = max(.01, size[2])
            if self.entity.model:
                pos = self.entity.model.getPos()
            self.shape = CollisionBox(pos, size[0], y, z)
        else:
            self.shape = CollisionBox(pos, .01, .01, .01)

        self.node_path = self.entity.attachNewNode(CollisionNode('CollisionNode'))
        self.node_path.node().addSolid(self.shape)
        self.entity.collision = True
        # self.node_path.show()

    def remove(self):
        self.node_path.removeNode()

if __name__ == '__main__':
    from pandaeditor import PandaEditor, Entity, color
    app = PandaEditor()
    e = Entity()
    e.model = 'quad'
    e.color = color.red
    e.collider = 'box'
    # e.origin = (-.5, -.5)
    # e.collider.remove()
    # e.collider = 'box'

    app.run()
