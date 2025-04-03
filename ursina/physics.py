"""
ursina/physics.py

This module provides physics handling for the Ursina engine using the Bullet physics library.
It includes classes for different shapes, rigid bodies, and a physics handler to manage the physics world.

Dependencies:
- panda3d.core.BitMask32
- panda3d.core.TransformState
- panda3d.bullet.BulletRigidBodyNode
- panda3d.bullet.BulletPlaneShape
- panda3d.bullet.BulletBoxShape
- panda3d.bullet.BulletSphereShape
- panda3d.bullet.BulletCylinderShape
- panda3d.bullet.BulletCapsuleShape
- panda3d.bullet.BulletConeShape
- panda3d.bullet.XUp
- panda3d.bullet.YUp
- panda3d.bullet.ZUp
- panda3d.bullet.BulletTriangleMesh
- panda3d.bullet.BulletTriangleMeshShape
- panda3d.bullet.BulletDebugNode
- panda3d.bullet.BulletWorld
- ursina.scripts.property_generator.generate_properties_for_class
- ursina.Entity
- ursina.scene
- ursina.time
- ursina.Vec3
"""

from panda3d.core import BitMask32, TransformState
from panda3d.bullet import BulletRigidBodyNode, BulletPlaneShape, BulletBoxShape, BulletSphereShape, BulletCylinderShape, BulletCapsuleShape, BulletConeShape, XUp, YUp, ZUp, BulletTriangleMesh, BulletTriangleMeshShape, BulletDebugNode, BulletWorld
from ursina.scripts.property_generator import generate_properties_for_class
from ursina import Entity, scene, time, Vec3

@generate_properties_for_class()
class _PhysicsHandler(Entity):
    """
    The _PhysicsHandler class manages the physics world and updates the physics simulation.

    Attributes:
        _debugNode (BulletDebugNode): The debug node for visualizing physics.
        debug_node_path (NodePath): The node path for the debug node.
        world (BulletWorld): The Bullet physics world.
        active (bool): Whether the physics simulation is active.
    """
    def __init__(self):
        """
        Initialize the _PhysicsHandler with default settings.
        """
        self._debugNode = BulletDebugNode('Debug')
        self._debugNode.showWireframe(True)
        self._debugNode.showConstraints(True)
        self._debugNode.showBoundingBoxes(False)
        self._debugNode.showNormals(False)
        self.debug_node_path = scene.attachNewNode(self._debugNode)

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, -9.806, 0))
        self.world.setDebugNode(self.debug_node_path.node())
        super().__init__()

        self.active = False

    def update(self):
        """
        Update the physics simulation if the handler is active.
        """
        if self.active:
            self.world.doPhysics(time.dt)
            # print("physics handler now active")

    def debug_setter(self, value):
        """
        Set the debug mode for the physics handler.

        Args:
            value (bool): Whether to enable debug mode.
        """
        if value:
            self.debug_node_path.show()
        else:
            self.debug_node_path.hide()

physics_handler = _PhysicsHandler()


class PlaneShape:
    """
    A class representing a plane shape for physics collisions.

    Attributes:
        center (tuple): The center of the plane.
        normal (Vec3): The normal vector of the plane.
        offset (float): The offset of the plane.
    """
    def __init__(self, center=(0,0,0), normal=Vec3(0,1,0), offset=0):
        """
        Initialize the PlaneShape with the specified center, normal, and offset.

        Args:
            center (tuple, optional): The center of the plane. Defaults to (0,0,0).
            normal (Vec3, optional): The normal vector of the plane. Defaults to Vec3(0,1,0).
            offset (float, optional): The offset of the plane. Defaults to 0.
        """
        self.center = center
        self.normal = normal
        self.offset = offset

class BoxShape:
    """
    A class representing a box shape for physics collisions.

    Attributes:
        center (tuple): The center of the box.
        size (tuple): The size of the box.
    """
    def __init__(self, center=(0,0,0), size=(1,1,1)):
        """
        Initialize the BoxShape with the specified center and size.

        Args:
            center (tuple, optional): The center of the box. Defaults to (0,0,0).
            size (tuple, optional): The size of the box. Defaults to (1,1,1).
        """
        self.center = center
        self.size = size

class SphereShape:
    """
    A class representing a sphere shape for physics collisions.

    Attributes:
        center (tuple): The center of the sphere.
        radius (float): The radius of the sphere.
    """
    def __init__(self, center=(0,0,0), radius=.5):
        """
        Initialize the SphereShape with the specified center and radius.

        Args:
            center (tuple, optional): The center of the sphere. Defaults to (0,0,0).
            radius (float, optional): The radius of the sphere. Defaults to .5.
        """
        self.center = center
        self.radius = radius

class CylinderShape:
    """
    A class representing a cylinder shape for physics collisions.

    Attributes:
        center (tuple): The center of the cylinder.
        radius (float): The radius of the cylinder.
        height (float): The height of the cylinder.
        axis (str): The axis of the cylinder ('x', 'y', or 'z').
    """
    def __init__(self, center=(0,0,0), radius=.5, height=2, axis='y'):
        """
        Initialize the CylinderShape with the specified center, radius, height, and axis.

        Args:
            center (tuple, optional): The center of the cylinder. Defaults to (0,0,0).
            radius (float, optional): The radius of the cylinder. Defaults to .5.
            height (float, optional): The height of the cylinder. Defaults to 2.
            axis (str, optional): The axis of the cylinder. Defaults to 'y'.
        """
        self.center = center
        self.radius = radius
        self.height = height
        self.axis = axis

class CapsuleShape:
    """
    A class representing a capsule shape for physics collisions.

    Attributes:
        center (tuple): The center of the capsule.
        radius (float): The radius of the capsule.
        height (float): The height of the capsule.
        axis (str): The axis of the capsule ('x', 'y', or 'z').
    """
    def __init__(self, center=(0,0,0), radius=.5, height=2, axis='y'):
        """
        Initialize the CapsuleShape with the specified center, radius, height, and axis.

        Args:
            center (tuple, optional): The center of the capsule. Defaults to (0,0,0).
            radius (float, optional): The radius of the capsule. Defaults to .5.
            height (float, optional): The height of the capsule. Defaults to 2.
            axis (str, optional): The axis of the capsule. Defaults to 'y'.
        """
        self.center = center
        self.radius = radius
        self.height = height
        self.axis = axis

class ConeShape:
    """
    A class representing a cone shape for physics collisions.

    Attributes:
        center (tuple): The center of the cone.
        radius (float): The radius of the cone.
        height (float): The height of the cone.
        axis (str): The axis of the cone ('x', 'y', or 'z').
    """
    def __init__(self, center=(0,0,0), radius=.5, height=2, axis='y'):
        """
        Initialize the ConeShape with the specified center, radius, height, and axis.

        Args:
            center (tuple, optional): The center of the cone. Defaults to (0,0,0).
            radius (float, optional): The radius of the cone. Defaults to .5.
            height (float, optional): The height of the cone. Defaults to 2.
            axis (str, optional): The axis of the cone. Defaults to 'y'.
        """
        self.center = center
        self.radius = radius
        self.height = height
        self.axis = axis

class MeshShape:
    """
    A class representing a mesh shape for physics collisions.

    Attributes:
        mesh (Mesh): The mesh of the shape.
        center (tuple): The center of the shape.
    """
    def __init__(self, mesh=None, center=(0,0,0)):
        """
        Initialize the MeshShape with the specified mesh and center.

        Args:
            mesh (Mesh, optional): The mesh of the shape. Defaults to None.
            center (tuple, optional): The center of the shape. Defaults to (0,0,0).
        """
        self.mesh = mesh
        self.center = center


class _PhysicsBody:
    """
    The _PhysicsBody class provides common functionality for physics bodies.

    Attributes:
        world (BulletWorld): The Bullet physics world.
        attached (bool): Whether the body is attached to the world.
        _visible (bool): Whether the body is visible.
        ignore_paused (bool): Whether the body ignores the paused state.
        animations (list): A list of animations for the body.
    """
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

    def __init__(self, name: str, world):
        """
        Initialize the _PhysicsBody with the specified name and world.

        Args:
            name (str): The name of the physics body.
            world (BulletWorld): The Bullet physics world.
        """
        self.world = world
        self.attached = False
        self._visible = False
        self.ignore_paused = False
        self.animations = []

    def __getattr__(self, attr):
        """
        Get the attribute from the node path's node.

        Args:
            attr (str): The attribute name.

        Returns:
            The attribute value.
        """
        return getattr(self.node_path.node(), attr)
        

    def attach(self):
        """
        Attach the physics body to the world.
        """
        if not self.attached:
            self.world.attachRigidBody(self.node_path.node())
            self.attached = True

    def detach(self):
        """
        Detach the physics body from the world.
        """
        if self.attached:
            self.world.removeRigidBody(self.node_path.node())
            self.attached = False

    def remove(self):
        """
        Remove the physics body from the world and delete the node path.
        """
        self.detach()
        self.node_path.removeNode()


    @property
    def visible(self):
        """
        Get the visibility of the physics body.

        Returns:
            bool: True if the body is visible, False otherwise.
        """
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        """
        Set the visibility of the physics body.

        Args:
            value (bool): True to make the body visible, False to hide it.
        """
        self._visible = value
        if value:
            self.node_path.show()
        else:
            self.node_path.hide()

    @property
    def position(self):
        """
        Get the position of the physics body.

        Returns:
            Vec3: The position of the body.
        """
        return Vec3(*self.node_path.getPos())

    @position.setter
    def position(self, value):
        """
        Set the position of the physics body.

        Args:
            value (Vec3): The new position of the body.
        """
        self.node_path.setPos(Vec3(value))

    @property
    def x(self):
        """
        Get the x-coordinate of the physics body.

        Returns:
            float: The x-coordinate of the body.
        """
        return self.node_path.getX()

    @x.setter
    def x(self, value):
        """
        Set the x-coordinate of the physics body.

        Args:
            value (float): The new x-coordinate of the body.
        """
        self.node_path.setX(value)

    @property
    def y(self):
        """
        Get the y-coordinate of the physics body.

        Returns:
            float: The y-coordinate of the body.
        """
        return self.node_path.getY()

    @y.setter
    def y(self, value):
        """
        Set the y-coordinate of the physics body.

        Args:
            value (float): The new y-coordinate of the body.
        """
        self.node_path.setY(value)

    @property
    def z(self):
        """
        Get the z-coordinate of the physics body.

        Returns:
            float: The z-coordinate of the body.
        """
        return self.node_path.getZ()

    @z.setter
    def z(self, value):
        """
        Set the z-coordinate of the physics body.

        Args:
            value (float): The new z-coordinate of the body.
        """
        self.node_path.setZ(value)

    @property
    def rotation(self):
        """
        Get the rotation of the physics body.

        Returns:
            Vec3: The rotation of the body.
        """
        rotation = self.node_path.getHpr()
        return Vec3(rotation[1], rotation[0], rotation[2])

    @rotation.setter
    def rotation(self, value):
        """
        Set the rotation of the physics body.

        Args:
            value (Vec3): The new rotation of the body.
        """
        self.node_path.setHpr(Vec3(value[1], value[0], value[2]))

    @property
    def scale(self):
        """
        Get the scale of the physics body.

        Returns:
            Vec3: The scale of the body.
        """
        scale = self.node_path.getScale()
        return Vec3(scale[0], scale[1], scale[2])

    @scale.setter
    def scale(self, value):
        """
        Set the scale of the physics body.

        Args:
            value (Vec3): The new scale of the body.
        """
        value = [e if e!=0 else .001 for e in value]
        self.node_path.setScale(value[0], value[1], value[2])

    def add_force(self, force, point=(0,0,0)):
        """
        Add a force to the physics body.

        Args:
            force (Vec3): The force to add.
            point (tuple, optional): The point of application. Defaults to (0,0,0).
        """
        self.node_path.node().setActive(True)
        if point != (0,0,0):
            self.node_path.node().applyForce(force, point)
        else:
            self.node_path.node().applyCentralForce(force)

    def apply_impulse(self, force, point=(0,0,0)):
        """
        Apply an impulse to the physics body.

        Args:
            force (Vec3): The impulse force to apply.
            point (tuple, optional): The point of application. Defaults to (0,0,0).
        """
        self.node_path.node().setActive(True)
        if point != (0,0,0):
            self.node_path.node().applyImpulse(force, point)
        else:
            self.node_path.node().applyCentralImpulse(force)


class RigidBody(_PhysicsBody):
    """
    The RigidBody class represents a rigid body in the physics world.

    Attributes:
        rigid_body_node (BulletRigidBodyNode): The Bullet rigid body node.
        node_path (NodePath): The node path for the rigid body.
    """
    def __init__(self, shape, world=physics_handler.world, entity=None, mass=0, kinematic=False, friction=.5, mask=0x1):
        """
        Initialize the RigidBody with the specified shape, world, entity, mass, kinematic state, friction, and mask.

        Args:
            shape: The shape of the rigid body.
            world (BulletWorld, optional): The Bullet physics world. Defaults to physics_handler.world.
            entity (Entity, optional): The associated entity. Defaults to None.
            mass (float, optional): The mass of the rigid body. Defaults to 0.
            kinematic (bool, optional): Whether the rigid body is kinematic. Defaults to False.
            friction (float, optional): The friction of the rigid body. Defaults to .5.
            mask (int, optional): The collision mask. Defaults to 0x1.
        """
        if world is physics_handler.world and not physics_handler.active:
            physics_handler.active = True
        super().__init__(name='RigidBody', world=world)
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

        if not isinstance(shape, (list, tuple)):    # add just one shape
            self.node_path.node().addShape(_convert_shape(shape, entity, dynamic=not self.rigid_body_node.isStatic()), TransformState.makePosHpr(shape.center, entity.getHpr()))
        else:    # add multiple shapes
            for s in shape:
                self.node_path.node().addShape(_convert_shape(s, entity, dynamic=not self.rigid_body_node.isStatic()), TransformState.makePosHpr(s.center, entity.getHpr()))

        self.attach()
        self.node_path.setPythonTag('Entity', entity)


def _convert_shape(shape, entity, dynamic=True):
    """
    Convert a shape to a Bullet shape.

    Args:
        shape: The shape to convert.
        entity (Entity): The associated entity.
        dynamic (bool, optional): Whether the shape is dynamic. Defaults to True.

    Returns:
        BulletShape: The converted Bullet shape.

    Raises:
        Exception: If the shape is not valid.
    """
    if isinstance(shape, PlaneShape):
        return BulletPlaneShape(shape.normal, shape.offset)

    elif isinstance(shape, BoxShape):
        return BulletBoxShape(Vec3(shape.size[0] / 2, shape.size[1] / 2, shape.size[2] / 2))

    elif isinstance(shape, SphereShape):
        return BulletSphereShape(shape.radius)

    elif isinstance(shape, CylinderShape):
        if shape.axis == 'y':
            axis = YUp
        elif shape.axis == 'z':
            axis = ZUp
        elif shape.axis == 'x':
            axis = XUp
        return BulletCylinderShape(shape.radius, shape.height, axis)

    elif isinstance(shape, CapsuleShape):
        if shape.axis == 'y':
            axis = YUp
        elif shape.axis == 'z':
            axis = ZUp
        elif shape.axis == 'x':
            axis = XUp
        return BulletCapsuleShape(shape.radius, shape.height-1, axis)

    elif isinstance(shape, ConeShape):
        if shape.axis == 'y':
            axis = YUp
        elif shape.axis == 'z':
            axis = ZUp
        elif shape.axis == 'x':
            axis = XUp
        return BulletConeShape(shape.radius, shape.height, axis)

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
    else:
        raise Exception("You did not specify a valid shape!")



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

    physics_handler.debug = True

    EditorCamera()
    app.run()
