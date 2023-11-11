from panda3d.core import BitMask32, TransformState
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape, BulletSphereShape, BulletCapsuleShape, XUp, YUp, ZUp, BulletTriangleMesh, BulletTriangleMeshShape, BulletDebugNode, BulletWorld
from ursina.vec3 import Vec3

class BoxShape:
    def __init__(self, center=(0,0,0), size=(1,1,1)):
        self.center = center
        self.size = size

class SphereShape:
    def __init__(self, center=(0,0,0), radius=.5):
        self.center = center
        self.radius = radius

class CapsuleShape:
    def __init__(self, center=(0,0,0), radius=.5, height=2, axis='y'):
        self.center = center
        self.radius = radius
        self.height = height
        self.axis = axis

class MeshShape:
    def __init__(self, mesh=None, center=(0,0,0)):
        self.mesh = mesh
        self.center = center


class PhysicsBody:
    def __init__(self, name: str, world):
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

    @property
    def position(self):
        return Vec3(*self.node_path.getPos())

    @position.setter
    def position(self, value):
    	self.node_path.setPos(Vec3(value))

    @property
    def rotation(self):
        rotation = self.node_path.getHpr()
        return Vec3(rotation[1], rotation[0], rotation[2])

    @rotation.setter
    def rotation(self, value):
    	self.node_path.setHpr(Vec3(value[1], value[0], value[2]))

    @property
    def scale(self):
        scale = self.node_path.getScale()
        return Vec3(scale[0], scale[1], scale[2])

    @scale.setter
    def scale(self, value):
        value = [e if e!=0 else .001 for e in value]
        self.node_path.setScale(value[0], value[1], value[2])


class Rigidbody(PhysicsBody):
    def __init__(self, world, shape, entity=None, mass=0, friction=.5, mask=0x1):
        super().__init__(name='Rigidbody', world=world)
        self.collision_node = BulletRigidBodyNode('Rigidbody')
        self.collision_node.setMass(mass)
        self.collision_node.setFriction(friction)

        if entity:
            self.node_path = entity.getParent().attachNewNode(self.collision_node)
            entity.reparentTo(self.node_path)
            self.position = entity.position
            entity.position = shape.center
            self.rotation = entity.rotation
        else:
            self.node_path = render.attachNewNode(self.collision_node)
        self.node_path.node().setIntoCollideMask(BitMask32(mask))


        if not isinstance(shape, (list, tuple)):    # add just one shape
            self.node_path.node().addShape(_convert_shape(shape, entity))
        else:    # add multiple shapes
            for s in shape:
                self.node_path.node().addShape(_convert_shape(s, entity), TransformState.makePos(s.center))

        self.attach()
        self.node_path.setPythonTag('Entity', entity)


def _convert_shape(shape, entity):
    if isinstance(shape, BoxShape):
        return BulletBoxShape(Vec3(shape.size[0] / 2, shape.size[1] / 2, shape.size[2] / 2))

    if isinstance(shape, SphereShape):
        return BulletSphereShape(shape.radius)

    if isinstance(shape, CapsuleShape):
        if shape.axis == 'y':
            axis = YUp
        elif shape.axis == 'z':
            axis = ZUp
        elif shape.axis == 'x':
            axis = XUp
        return BulletCapsuleShape(shape.radius / 2, shape.height / 2, axis)

    if isinstance(shape, MeshShape) and entity:
        if shape.mesh is None and entity.model:
            mesh = entity.model
        else:
            mesh = shape.mesh

        geom_target = mesh.findAllMatches('**/+GeomNode').getPath(0).node().getGeom(0)
        output = BulletTriangleMesh()
        output.addGeom(geom_target)

        return BulletTriangleMeshShape(output, dynamic=True)
    else:
        raise Exception('To use a mesh shape you must specify at least one entity or mesh!')



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
