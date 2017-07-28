from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.core import NodePath
from panda3d.core import Vec3


class Collider(BulletRigidBodyNode):
    def __init__(self):
        super().__init__('empty')
        self.parent = None
        self.shape = None
        self.position = (0,0,0)
        self.rotation = (0,0,0)
        self.scale = (0,0,0)


    def remove(self):
        pass
        # self.removeNode()


    def __setattr__(self, name, value):
        # print(NodePath(self))
        # if name == 'parent':
        #     self.parent = value
        # else:
        super().__setattr__(name, value)

        if name == 'parent' and value != None:
            pass
            NodePath(self).reparentTo(value)

        # shape = BulletPlaneShape(Vec3(0, 0, 0), 1)
        if name == 'shape':
            if value == 'box':
                if self.parent.model:
                    min, max = self.parent.model.getTightBounds()
                    size = (max - min)
                    print('size:' , size)
                else:
                    size = Vec3(1,1,1)
                self.shape = BulletBoxShape(size / 2)
                self.addShape(self.shape)

        if name == 'scale':
            pass
            # self.shape = BulletBoxShape(Vec3(value[0], value[1], value[2]))
            # self.setScale(value[0], value[1], value[2])


        if name == 'position':
            if self.parent:
                np = self.parent.attachNewNode(self)
                np.setPos(value[0], value[1], value[2])
