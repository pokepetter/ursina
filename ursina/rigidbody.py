from panda3d.core import BitMask32, TransformState
from panda3d.bullet import BulletRigidBodyNode, BulletPlaneShape, BulletBoxShape, BulletSphereShape, BulletCapsuleShape, XUp, YUp, ZUp, BulletTriangleMesh, BulletTriangleMeshShape, BulletDebugNode, BulletWorld
from ursina.vec3 import Vec3

class PlaneShape:
    def __init__(self, normal=Vec3(0,1,0), offset=0):
        self.center = (0,0,0)
        self.normal = normal
        self.offset = offset

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

    def __getattr__(self, attribute):
        return getattr(self.node_path.node(), attribute)

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
    def x(self):
        return self.node_path.getX()

    @x.setter
    def x(self, value):
        self.node_path.setX(value)

    @property
    def y(self):
        return self.node_path.getY()

    @y.setter
    def y(self, value):
        self.node_path.setY(value)

    @property
    def z(self):
        return self.node_path.getZ()

    @z.setter
    def z(self, value):
        self.node_path.setZ(value)

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


class RigidBody(PhysicsBody):
    def __init__(self, world, shape, entity=None, mass=0, kinematic=False, friction=.5, mask=0x1):
        super().__init__(name='RigidBody', world=world)
        self.rigid_body_node = BulletRigidBodyNode('RigidBody')
        self.rigid_body_node.setMass(mass)
        self.rigid_body_node.setKinematic(kinematic)
        self.rigid_body_node.setFriction(friction)

        if entity:
            self.node_path = entity.getParent().attachNewNode(self.rigid_body_node)
            self.scale = entity.world_scale
            entity.reparentTo(self.node_path)
            self.position = entity.position
            entity.position = shape.center
            self.rotation = entity.rotation
            entity.world_scale = self.scale
        else:
            self.node_path = render.attachNewNode(self.rigid_body_node)
        self.node_path.node().setIntoCollideMask(BitMask32(mask))

        if not isinstance(shape, (list, tuple)):    # add just one shape
            self.node_path.node().addShape(_convert_shape(shape, entity, dynamic=not self.rigid_body_node.isStatic()))
        else:    # add multiple shapes
            for s in shape:
                self.node_path.node().addShape(_convert_shape(s, entity, dynamic=not self.rigid_body_node.isStatic()), TransformState.makePos(s.center))

        self.attach()
        self.node_path.setPythonTag('Entity', entity)


def _convert_shape(shape, entity, dynamic=True):
    if isinstance(shape, PlaneShape):
        return BulletPlaneShape(shape.normal, shape.offset)

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

        return BulletTriangleMeshShape(output, dynamic=dynamic)
    else:
        raise Exception('To use a mesh shape you must specify at least one entity or mesh!')



if __name__ == '__main__':
    from ursina import *

    app = Ursina(borderless=False)

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
    RigidBody(world=world, shape=PlaneShape(), entity=ground)

    cube = Entity(model='cube', texture='white_cube', y=7)
    RigidBody(world=world, shape=BoxShape(), entity=cube, mass=1)

    sphere = Entity(model='sphere', texture='brick', y=30)
    RigidBody(world=world, shape=SphereShape(), entity=sphere, mass=5)

    capsule = Entity(model='sphere', texture='brick', y=17, scale=(1,2,1))
    RigidBody(world=world, shape=CapsuleShape(height=2, radius=1), entity=capsule, mass=3)

    platform = Entity(model='cube', texture='white_cube', y=1, scale=(4, 1, 4))
    platform_body = RigidBody(world, BoxShape(), entity=platform, kinematic=True, friction=1.0)
    platform.positions = {
        'A': Vec3(-2, 1, -2),
        'B': Vec3(2, 1, -2),
        'C': Vec3(0, 1, 2)
    }
    platform.state_table = {
        'A': 'B',
        'B': 'C',
        'C': 'A'
    }
    platform.state = 'A'
    platform.time_passed = 0.0
    platform.move_time = 2.0

    def update():
        platform.time_passed += time.dt
        platform_body.position = lerp(platform.positions[platform.state], platform.positions[platform.state_table[platform.state]], clamp(platform.time_passed / platform.move_time, 0, 1))
        if platform.time_passed > platform.move_time:
            platform.state = platform.state_table[platform.state]
            platform.time_passed = 0.0
        world.doPhysics(time.dt)

    def input(key):
        if key == 'space up':
            spawned_cube = Entity(model='cube', texture='white_cube', y=7)
            RigidBody(world, BoxShape(), entity=spawned_cube, mass=1, friction=1.0)

    EditorCamera()

    app.run()
