from panda3d.core import NodePath, BitMask32, TransformState
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape, BulletSphereShape, BulletCapsuleShape, XUp, YUp, ZUp, BulletTriangleMesh, BulletTriangleMeshShape, BulletDebugNode, BulletWorld
from ursina.shapes import *
from ursina.vec3 import Vec3

class Body(NodePath):
    def __init__(self, name: str, world):
        super().__init__(name)
        self.world = world
        self.attached = False
        self._visible = False

    def attach(self):
        if not self.attached:
            self.world.attachRigidBody(self.node_path.node())
            self.attached = True

    def detach(self):
        if self.attached:
            self.world.removeRigidBody(self.node_path.node())
            self.attached = False

    def remove(self):
        self.detach()
        self.node_path.removeNode()

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        self._visible = value
        if value:
            self.node_path.show()
        else:
            self.node_path.hide()


class Rigidbody(Body):
    def __init__(self, world, shape, entity=None, mass=0, friction=.5, mask=0x1):
        super().__init__(name='Rigidbody', world=world)
        self.collision_node = BulletRigidBodyNode('Rigidbody')
        self.collision_node.setMass(mass)
        self.collision_node.setFriction(friction)
        self.node_path = entity.getParent().attachNewNode(self.collision_node)

        self.shape_infos = shape.getProperties()

        if self.shape_infos['shape'] == 'box':
            self.shape = BulletBoxShape(Vec3(self.shape_infos['size'][0] / 2, self.shape_infos['size'][1] / 2, self.shape_infos['size'][2] / 2))
            self.node_path.node().addShape(self.shape)

        elif self.shape_infos['shape'] == 'sphere':
            self.shape = BulletSphereShape(self.shape_infos['radius'])
            self.node_path.node().addShape(self.shape)

        elif self.shape_infos['shape'] == 'capsule':
            if self.shape_infos['axis'] == 'y':
                axis = YUp
            elif self.shape_infos['axis'] == 'z':
                axis = ZUp
            elif self.shape_infos['axis'] == 'x':
                axis = XUp
            self.shape = BulletCapsuleShape(self.shape_infos['radius'] / 2, self.shape_infos['height'] / 2, axis)
            self.node_path.node().addShape(self.shape)

        elif self.shape_infos['shape'] == 'mesh':
            if self.shape_infos['mesh'] == None and entity.model:
                mesh = entity.model
            else:
                mesh = self.shape_infos['mesh']

            geom_target = mesh.findAllMatches('**/+GeomNode').getPath(0).node().getGeom(0)
            output = BulletTriangleMesh()
            output.addGeom(geom_target)

            self.shape = BulletTriangleMeshShape(output, dynamic=True)
            self.node_path.node().addShape(self.shape)

        elif self.shape_infos['shape'] == 'compound':
            for s in self.shape_infos['shapes']:
                if s['shape'] == 'box':
                    self.shape = BulletBoxShape(Vec3(s['size'][0] / 2, s['size'][1] / 2, s['size'][2] / 2))
                elif s['shape'] == 'sphere':
                    self.shape = BulletSphereShape(s['radius'])
                elif s['shape'] == 'capsule':
                    if s['axis'] == 'y':
                        axis = YUp
                    elif s['axis'] == 'z':
                        axis = ZUp
                    elif s['axis'] == 'x':
                        axis = XUp
                    self.shape = BulletCapsuleShape(s['radius'] / 2, s['height'] / 2, axis)
                elif s['shape'] == 'mesh':
                    if self.shape_infos['mesh'] == None and entity.model:
                        mesh = entity.model
                    else:
                        mesh = self.shape_infos['mesh']

                    geom_target = mesh.findAllMatches('**/+GeomNode').getPath(0).node().getGeom(0)
                    output = BulletTriangleMesh()
                    output.addGeom(geom_target)

                    self.shape = BulletTriangleMeshShape(output, dynamic=True)

                self.node_path.node().addShape(self.shape, TransformState.makePos(s['center']))

        self.node_path.node().setIntoCollideMask(BitMask32(mask))
        entity.reparentTo(self.node_path)
        self.node_path.setPos(entity.x, entity.y, entity.z)
        self.attach()
        entity.position = self.shape_infos['center']

        self.node_path.setPythonTag('Entity', entity)


if __name__ == '__main__':
    from ursina import *

    app = Ursina()

    debugNode = BulletDebugNode('Debug')
    debugNode.showWireframe(True)
    debugNode.showConstraints(True)
    debugNode.showBoundingBoxes(False)
    debugNode.showNormals(False)
    debugNP = render.attachNewNode(debugNode)
    debugNP.show()
    
    world = BulletWorld()
    world.setGravity(Vec3(0, -9.81, 0))
    world.setDebugNode(debugNP.node())

    ground = Entity(model='plane', texture='grass', y=0, scale=30)
    Rigidbody(world=world, shape=BoxShape(size=(30,.05,30)), entity=ground)

    cube = Entity(model='cube', texture='white_cube', y=7)
    Rigidbody(world=world, shape=BoxShape(), entity=cube, mass=1)

    sphere = Entity(model='sphere', texture='brick', y=30)
    Rigidbody(world=world, shape=SphereShape(), entity=sphere, mass=5)

    capsule = Entity(model='sphere', texture='brick', y=17, scale=(1,2,1))
    Rigidbody(world=world, shape=CapsuleShape(height=2, radius=1), entity=capsule, mass=3)

    def update():
        world.doPhysics(time.dt)


    EditorCamera()

    app.run()