from panda3d.core import CollisionNode, CollisionBox, CollisionSphere, CollisionPolygon
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

    @visible.setter
    def visible(self, value):
        if value:
            self.node_path.show()
        else:
            self.node_path.hide()
            pass


class BoxCollider(Collider):
    def __init__(self, entity, center=(0,0,0), size=(1,1,1)):
        super().__init__()
        size = [e/2 for e in size]
        size = [max(0.001, e) for e in size] # collider needs to have thickness
        self.shape = CollisionBox(Vec3(center[0], center[2], center[1]), size[0], size[2], size[1])
        # self.remove()
        self.node_path = entity.attachNewNode(CollisionNode('CollisionNode'))
        self.node_path.node().addSolid(self.shape)
        self.visible = False
        # self.node_path.show()
        # for some reason self.node_path gets removed after this and can't be shown.

class SphereCollider(Collider):
    def __init__(self, entity, center=(0,0,0), radius=.5):
        super().__init__()
        self.shape = CollisionSphere(center[0], center[2], center[1], radius)
        self.node_path = entity.attachNewNode(CollisionNode('CollisionNode'))
        self.node_path.node().addSolid(self.shape)
        self.visible = False


class MeshCollider(Collider):
    def __init__(self, entity, mesh=None, center=(0,0,0)):
        super().__init__()
        center = Vec3(center)
        if mesh == None and entity.model:
            print('auto gen mesh colider from entity mesh')
            mesh = entity.model

        self.node_path = entity.attachNewNode(CollisionNode('CollisionNode'))
        self.node_path.setP(90)
        node = self.node_path.node()

        if mesh.triangles:
            for tri in mesh.triangles:
                if len(tri) == 3:
                    shape = CollisionPolygon(
                        Vec3(mesh.vertices[tri[0]]) + center,
                        Vec3(mesh.vertices[tri[1]]) + center,
                        Vec3(mesh.vertices[tri[2]]) + center)
                    node.addSolid(shape)
                elif len(tri) == 4:
                    shape = CollisionPolygon(
                        Vec3(mesh.vertices[tri[0]]) + center,
                        Vec3(mesh.vertices[tri[1]]) + center,
                        Vec3(mesh.vertices[tri[2]]) + center)
                    node.addSolid(shape)
                    shape = CollisionPolygon(
                        Vec3(mesh.vertices[tri[2]]) + center,
                        Vec3(mesh.vertices[tri[3]]) + center,
                        Vec3(mesh.vertices[tri[0]]) + center)
                    node.addSolid(shape)

        elif mesh.mode == 'triangle':
            for i in range(0, len(mesh.vertices), 3):
                shape = CollisionPolygon(
                    Vec3(mesh.vertices[i]) + center,
                    Vec3(mesh.vertices[i+1]) + center,
                    Vec3(mesh.vertices[i+2]) + center
                    )
                node.addSolid(shape)

        else:
            print('error: mesh collider does not support', mesh.mode, 'mode')


        self.visible = False


if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    c = Cylinder(6, height=1, start=-.5)
    c = Prismatoid(base_shape=Circle(6), thicknesses=(1, .5))
    e = Button(parent=scene, model=c, collider='mesh', color=color.red, highlight_color=color.yellow)
    # e.collider = MeshCollider(e)
    # printvar(e.collider.node_path)
    # e.collider.visible = True
    # def update():
    #     print(mouse.hovered_entity)

    EditorCamera()
    app.run()
