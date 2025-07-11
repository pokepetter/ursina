from panda3d.core import BitMask32, TransformState
from panda3d.bullet import BulletRigidBodyNode, BulletPlaneShape, BulletBoxShape, BulletSphereShape, BulletCylinderShape, BulletCapsuleShape, BulletConeShape, XUp, YUp, ZUp, BulletTriangleMesh, BulletTriangleMeshShape, BulletDebugNode, BulletWorld
from ursina.scripts.property_generator import generate_properties_for_class
from ursina.entity import Entity
from ursina import scene, time
from ursina.vec3 import Vec3

class PhysicsHandler(Entity):
    def __init__(self):
        self._debug_node = BulletDebugNode('Debug')
        self._debug_node.showWireframe(True)
        self._debug_node.showConstraints(True)
        self._debug_node.showBoundingBoxes(False)
        self._debug_node.showNormals(False)
        self.debug_node_path = scene.attachNewNode(self._debug_node)

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, -9.81, 0))
        self.world.setDebugNode(self.debug_node_path.node())
        super().__init__()

        self.active = False
        self._show_debug = False

    def update(self):
        if self.active:
            self.world.doPhysics(time.dt)
            # print("physics handler now active")

    @property
    def show_debug(self):
        return self._show_debug

    @show_debug.setter
    def show_debug(self, value):
        self._show_debug = value
        if value:
            self.debug_node_path.show()
        else:
            self.debug_node_path.hide()
physics_handler = PhysicsHandler()


class PlaneShape:
    def __init__(self, center=(0,0,0), normal=Vec3(0,1,0), offset=0):
        self.center = center
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

class CylinderShape:
    def __init__(self, center=(0,0,0), radius=.5, height=2, axis='y'):
        self.center = center
        self.radius = radius
        self.height = height
        self.axis = axis

class CapsuleShape:
    def __init__(self, center=(0,0,0), radius=.5, height=2, axis='y'):
        self.center = center
        self.radius = radius
        self.height = height
        self.axis = axis

class ConeShape:
    def __init__(self, center=(0,0,0), radius=.5, height=2, axis='y'):
        self.center = center
        self.radius = radius
        self.height = height
        self.axis = axis

class MeshShape:
    def __init__(self, mesh=None, center=(0,0,0)):
        self.mesh = mesh
        self.center = center


@generate_properties_for_class(getter_suffix='_getter', setter_suffix='_setter')
class _PhysicsBody:
    # Copy animation functions from Entity
    animate = Entity.animate

    animate_position = Entity.animate_position
    animate_x = Entity.animate_x
    animate_y = Entity.animate_y
    animate_z = Entity.animate_z

    animate_rotation = Entity.animate_rotation
    animate_rotation_x = Entity.animate_rotation_x
    animate_rotation_y = Entity.animate_rotation_y
    animate_rotation_z = Entity.animate_rotation_z

    animate_scale = Entity.animate_scale
    animate_scale_x = Entity.animate_scale_x
    animate_scale_y = Entity.animate_scale_y
    animate_scale_z = Entity.animate_scale_z

    _getattr = Entity._getattr
    _setattr = Entity._setattr

    def __init__(self):
        self._visible = False
        self.ignore_paused = False
        self.animations = []

    def __getattr__(self, attribute):
        return getattr(self.node_path.node(), attribute)
        

    def visible_getter(self):
        return self._visible

    def visible_setter(self, value):
        self._visible = value
        if value:
            self.node_path.show()
        else:
            self.node_path.hide()

    def position_getter(self):
        return Vec3(*self.node_path.getPos())

    def position_setter(self, value):
        self.node_path.setPos(Vec3(value))

    def x_getter(self):
        return self.node_path.getX()

    def x_setter(self, value):
        self.node_path.setX(value)

    def y_getter(self):
        return self.node_path.getY()

    def y_setter(self, value):
        self.node_path.setY(value)

    def z_getter(self):
        return self.node_path.getZ()

    def z_setter(self, value):
        self.node_path.setZ(value)

    def rotation_getter(self):
        rotation = self.node_path.getHpr()
        return Vec3(rotation[1], rotation[0], rotation[2])

    def rotation_setter(self, value):
        self.node_path.setHpr(Vec3(value[1], value[0], value[2]))

    def scale_getter(self):
        scale = self.node_path.getScale()
        return Vec3(scale[0], scale[1], scale[2])

    def scale_setter(self, value):
        value = [e if e!=0 else .001 for e in value]
        self.node_path.setScale(value[0], value[1], value[2])

    def add_force(self, force, point=(0,0,0)):
        self.node_path.node().setActive(True)
        if point != (0,0,0):
            self.node_path.node().applyForce(force, point)
        else:
            self.node_path.node().applyCentralForce(force)

    def apply_impulse(self, force, point=(0,0,0)):
        self.node_path.node().setActive(True)
        if point != (0,0,0):
            self.node_path.node().applyImpulse(force, point)
        else:
            self.node_path.node().applyCentralImpulse(force)


class RigidBody(_PhysicsBody):
    def __init__(self, shape, world=physics_handler.world, entity=None, mass=0, kinematic=False, friction=.5, mask=0x1):
        super().__init__()
        self.world = world
        if self.world is physics_handler.world and not physics_handler.active:
            physics_handler.active = True

        self.rigid_body_node = BulletRigidBodyNode('RigidBody')
        self.rigid_body_node.setMass(mass)
        self.rigid_body_node.setKinematic(kinematic)
        self.rigid_body_node.setFriction(friction)

        if entity:
            self.node_path = entity.getParent().attachNewNode(self.rigid_body_node)
            self.scale = entity.world_scale
            self.position = entity.world_position
            entity.world_parent = self.node_path
        else:
            self.node_path = render.attachNewNode(self.rigid_body_node)
        self.node_path.node().setIntoCollideMask(BitMask32(mask))

        if isinstance(shape, (list, tuple)):
            for s in shape:
                self.node_path.node().addShape(_convert_shape(s, entity, dynamic=not self.rigid_body_node.isStatic()), TransformState.makePosHpr(s.center, entity.getHpr()))
        else:
            self.node_path.node().addShape(_convert_shape(shape, entity, dynamic=not self.rigid_body_node.isStatic()), TransformState.makePosHpr(shape.center, entity.getHpr()))

        self.world.attachRigidBody(self.node_path.node())
        self.node_path.setPythonTag('Entity', entity)

    def remove(self):
        self.world.removeRigidBody(self.node_path.node())
        self.node_path.removeNode()


def _convert_shape(shape, entity, dynamic=True):
    if isinstance(shape, PlaneShape):
        return BulletPlaneShape(shape.normal, shape.offset)

    elif isinstance(shape, BoxShape):
        return BulletBoxShape(Vec3(shape.size[0]/2, shape.size[1]/2, shape.size[2]/2))

    elif isinstance(shape, SphereShape):
        return BulletSphereShape(shape.radius)

    elif isinstance(shape, MeshShape):
        if entity:
            if shape.mesh is None and entity.model:
                mesh = entity.model
            else:
                mesh = shape.mesh

            geom_target = mesh.findAllMatches('**/+GeomNode').getPath(0).node().getGeom(0)
            output = BulletTriangleMesh()
            output.addGeom(geom_target)

            return BulletTriangleMeshShape(output, dynamic=dynamic)

    elif isinstance(shape, CapsuleShape):
        if shape.axis == 'y':
            axis = YUp
        elif shape.axis == 'z':
            axis = ZUp
        elif shape.axis == 'x':
            axis = XUp
        return BulletCapsuleShape(shape.radius, shape.height-1, axis)

    elif isinstance(shape, CylinderShape):
        if shape.axis == 'y':
            axis = YUp
        elif shape.axis == 'z':
            axis = ZUp
        elif shape.axis == 'x':
            axis = XUp
        return BulletCylinderShape(shape.radius, shape.height, axis)

    elif isinstance(shape, ConeShape):
        if shape.axis == 'y':
            axis = YUp
        elif shape.axis == 'z':
            axis = ZUp
        elif shape.axis == 'x':
            axis = XUp
        return BulletConeShape(shape.radius, shape.height, axis)
    else:
        raise Exception("invalid shape.")



if __name__ == '__main__':
    from ursina import Ursina, Cylinder, Capsule, Cone, Sequence, Func, curve, Wait, EditorCamera

    app = Ursina(borderless=False)

    ground = Entity(model='plane', texture='grass', scale=30)
    RigidBody(shape=PlaneShape(), entity=ground)

    cube = Entity(model='cube', texture='white_cube')
    # cube.rotation = Vec3(0,45,68)
    # cube.scale = Vec3(.5)
    cube.y = 7
    cube_body = RigidBody(shape=BoxShape(), entity=cube, mass=1)

    sphere = Entity(model='sphere', texture='brick', y=30)
    RigidBody(shape=SphereShape(), entity=sphere, mass=5)

    cylinder = Entity(model=Cylinder(height=2, radius=.5, start=-1), texture='brick', y=17)
    RigidBody(shape=CylinderShape(height=2, radius=.5), entity=cylinder, mass=3)

    capsule = Entity(model=Capsule(height=2, radius=.5), texture='brick', y=15)
    RigidBody(shape=CapsuleShape(height=2, radius=.5), entity=capsule, mass=3)

    cone = Entity(model=Cone(resolution=8, height=2, radius=.5), texture='brick', y=13)
    RigidBody(shape=ConeShape(height=2, radius=.5), entity=cone, mass=2)

    platform = Entity(model='cube', texture='white_cube', y=1, scale=(4,1,4))
    platform_body = RigidBody(shape=BoxShape(), entity=platform, kinematic=True, friction=1)
    platform_sequence = Sequence(entity=platform, loop=True)

    path = [Vec3(-2,1,-2), Vec3(2,1,-2), Vec3(0, 1, 2)]
    travel_time = 2
    for target_pos in path:
        platform_sequence.append(Func(platform_body.animate_position, value=target_pos, duration=travel_time, curve=curve.linear), regenerate=False)
        platform_sequence.append(Wait(travel_time), regenerate=False)
    platform_sequence.generate()
    platform_sequence.start()


    def input(key):
        if key == 'space up':
            e = Entity(model='cube', texture='white_cube', y=7)
            RigidBody(shape=BoxShape(), entity=e, mass=1, friction=1)
        if key == 'up arrow':
            cube_body.apply_impulse(force=Vec3(0, 10, 0), point=Vec3(0,0,0))
            print('impulse applied')

    physics_handler.show_debug = True

    EditorCamera()
    app.run()
