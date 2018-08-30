from panda3d.core import CollisionNode, CollisionBox, CollisionSphere
from panda3d.core import NodePath
from panda3d.core import Vec3

class Collider(NodePath):
    def __init__(self):
        super().__init__('box_collider')

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def remove(self):
        self.node_path.removeNode()

    @property
    def visible(self):
        return self._visible

    def visible(self, value):
        if value:
            self.node_path.show()
        else:
            self.node_path.hide()


class BoxCollider(Collider):
    def __init__(self, entity, center=(0,0,0), size=(1,1,1)):
        super().__init__()
        size = [e/2 for e in size]
        size = [max(0.01, e) for e in size] # collider needs to have thickness
        self.shape = CollisionBox(Vec3(center[0], center[2], center[1]), size[0], size[2], size[1])
        self.node_path = entity.attachNewNode(CollisionNode('CollisionNode'))
        self.node_path.node().addSolid(self.shape)
        self.visible = False


class SphereCollider(Collider):
    def __init__(self, entity, center=(0,0,0), radius=.5):
        super().__init__()
        self.shape = CollisionSphere(center[0], center[2], center[1], radius)
        self.node_path = entity.attachNewNode(CollisionNode('CollisionNode'))
        self.node_path.node().addSolid(self.shape)
        self.visible = False


if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    e = Button(parent=scene, model='cube', collider='box')
    e.color = color.red
    EditorCamera()
    app.run()
