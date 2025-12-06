from panda3d.core import BitMask32, TransformState
from panda3d.bullet import BulletRigidBodyNode, BulletPlaneShape, BulletBoxShape, BulletSphereShape, BulletCylinderShape, BulletCapsuleShape, BulletConeShape, XUp, YUp, ZUp, BulletTriangleMesh, BulletTriangleMeshShape, BulletDebugNode, BulletWorld
from ursina.scripts.property_generator import generate_properties_for_class
from ursina.entity import Entity
from ursina import scene, time, color
from ursina.vec3 import Vec3
from copy import copy
from ursina.mesh import Mesh
from ursina.destroy import destroy

@generate_properties_for_class()
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

        self.active = True
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

    def gravity_setter(self, value):
        self._gravity = value
        if isinstance(value, float | int):
            value = Vec3.down * value
        self.world.setGravity(value)

physics_handler = PhysicsHandler()


def PlaneCollider(center=Vec3.zero, normal=Vec3.up, offset=0):
    return BulletPlaneShape(normal, offset)
def BoxCollider(center=Vec3.zero, size=Vec3.one):
    return BulletBoxShape(Vec3(*size)/2)
def SphereCollider(center=Vec3.zero, radius=.5):
    return BulletSphereShape(radius)

def CapsuleCollider(radius=.5, height=2, center=(0,0,0), axis='y'):
    if axis == 'y':         axis = YUp
    elif axis == 'z':       axis = ZUp
    elif axis == 'x':       axis = XUp
    return BulletCapsuleShape(radius, height-1, axis)

def MeshCollider(mesh):
    geom_target = mesh.findAllMatches('**/+GeomNode').getPath(0).node().getGeom(0)
    output = BulletTriangleMesh()
    output.addGeom(geom_target)
    return BulletTriangleMeshShape(output, dynamic=False)



_line_model = Mesh(vertices=[Vec3(0,0,0), Vec3(0,0,1)], mode='line')
from ursina.hit_info import HitInfo

def raycast(origin, direction: Vec3 = Vec3(0, 0, 1), distance=9999,
            traverse_target=None, ignore: list = None, debug=False, color=color.white):
    world = physics_handler.world
    from_pos = origin
    to_pos = origin + (direction * distance)

    if not ignore:
        result = world.rayTestClosest(from_pos, to_pos)
        hit = result.hasHit()
    else:
        all_results = world.rayTestAll(from_pos, to_pos)

        # convert entities to their Bullet nodes if needed
        ignored_nodes = set()
        for obj in ignore:
            if hasattr(obj, "_node"):
                ignored_nodes.add(obj._node)
            else:
                ignored_nodes.add(obj)

        valid_hits = [h for h in all_results.getHits() if h.getNode() not in ignored_nodes]

        if not valid_hits:
            return HitInfo()  # no valid hits

        valid_hits.sort(key=lambda h: h.getHitFraction())
        result = valid_hits[0]
        hit = True

    if debug or physics_handler.show_debug:
        temp = Entity(position=origin, model=copy(_line_model), scale=Vec3(1, 1, min(distance, 9999)), color=color, add_to_scene_entities=1)
        temp.look_at(to_pos)
        destroy(temp, delay=1/30)

    if not hit:
        return HitInfo(hit=False)

    return HitInfo(
        hit=True,
        entity=result.getNode(),
        point=result.getHitPos(),
        world_point=result.getHitPos(),
        distance=result.getHitFraction() * distance,
        normal=result.getHitNormal(),
        world_normal=result.getHitNormal(),
        hits=None,
        entities=None
    )



from ursina import Vec2, Default
@generate_properties_for_class()
class PhysicsEntity:
    rb_reserved_args = ('mass', 'kinematic', 'friction', 'mask', 'world', 'lock_axis', 'lock_rotation', 'velocity',
                # 'rotation', 'rotation_x', 'rotation_y', 'rotation_z',  # for some reason setting the rigidbody's rotation makes it choppy, so only do it for kinematic bodies..
                )
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
    look_at_2d = Entity.look_at_2d
    look_at_xy = Entity.look_at_xy
    look_at_xz = Entity.look_at_xz
    look_in_direction = Entity.look_in_direction
    look_at = Entity.look_at
    _list_to_vec = Entity._list_to_vec

    def __init__(self, mass=0, kinematic=None, friction=.5, mask=0x1, collider=None, world=physics_handler.world, lock_axis=Vec3.zero, lock_rotation=Vec3.zero,
            enabled=True,
            # parent=scene,
            **kwargs):

        self.world = world

        entity_kwargs = {key : value for key, value in kwargs.items() if key not in __class__.rb_reserved_args}
        self.entity = Entity(add_to_scene_entities=False, **entity_kwargs)
        # self.entity.wireframe = True

        # create an rb node next to the entity and reparent the entity to the rb node, since the rb node should control it.
        self.node = BulletRigidBodyNode('RigidBody')
        # node_to_attach_to = self.entity.parent
        # if node_to_attach_to == scene:
        kinematic = kinematic if kinematic is not None else (mass == 0)
        if kinematic:   # allow parenting
            self.rb = self.entity.parent.attachNewNode(self.node) # node path
        else:
            self.rb = scene.attachNewNode(self.node) # node path


        self.rb.setPythonTag('Entity', self.entity)
        self.hasPythonTag = self.rb.hasPythonTag

        self.collider = collider # set collider before resetting entity, since we need to get scale. we can't scale rb nodes
        if kinematic:
            self.position = self.entity.position - self.entity.origin
            self.rotation = self.entity.rotation
            self.scale = self.entity.scale
        else: # simulated rigidbodies can't be parented, so use world transform
            self.position = self.entity.world_position - (self.entity.origin * self.entity.world_scale)
            self.rotation = self.entity.world_rotation
            self.scale = self.entity.world_scale

        # since the entity is now parented to the rigidbody, reset the transform
        self.entity.parent = self.rb
        self.entity.position = Vec3.zero
        self.entity.rotation = Vec3.zero
        self.entity.scale = Vec3.one
        self.entity.origin = Vec3.zero

        self.mass = mass
        self.kinematic = kinematic
        self.friction = friction
        self.node.setIntoCollideMask(BitMask32(mask))
        self.lock_rotation = lock_rotation
        self.lock_axis = lock_axis

        self.enabled = enabled
        self.ignore = False
        self.ignore_input = False
        self.collision = True
        self.eternal = False
        self.ignore_paused = False
        self.animations = []
        self.animate = self.entity.animate
        scene.entities.append(self)
        self.forward = self.entity.forward
        self.back = self.entity.back
        self.right = self.entity.right
        self.left = self.entity.left
        self.up = self.entity.up
        self.down = self.entity.down
        self.screen_position = self.entity.screen_position
        self.get_tight_bounds = self.entity.get_tight_bounds
        self.blink = self.entity.blink
        self.has_ancestor = self.entity.has_ancestor
        self.hasPythonTag = self.entity.hasPythonTag
        self.clearPythonTag = self.entity.clearPythonTag
        self.children = []

        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

    def removeNode(self):   # for destroy() compatibility
        self.world.removeRigidBody(self.node)
        self.rb.removeNode()

    def parent_target_getter(self):
        return self.entity

    def loose_children_getter(self):
        return self.entity.loose_children

    def has_disabled_ancestor(self):
        return self.entity.has_disabled_ancestor()


    def parent_setter(self, value):
        self._parent = value
        self.rb.reparentTo(value)

    def model_getter(self):
        return self.entity.model
    def model_setter(self, value):
        self.entity.model = value

    def origin_getter(self):
        return self.entity.origin
    def origin_setter(self, value):
        self.entity.origin = value

    def shader_getter(self): return self.entity.shader
    def shader_setter(self, value):
        self.entity.shader = value
    def set_shader_input(self, key, value):
        self.entity.set_shader_input(key, value)



    # for rigidbody
    def position_getter(self):
        return Vec3(*self.rb.getPos())
    def position_setter(self, value):
        self.rb.setPos(Vec3(value))

    def world_position_getter(self):
        return Vec3(*self.rb.getPos(scene))
    def world_position_setter(self, value):
        self.rb.setPos(scene, Vec3(value[0], value[1], value[2]))

    def x_getter(self):
        return self.rb.getX()
    def x_setter(self, value):
        self.rb.setX(value)

    def y_getter(self):
        return self.rb.getY()
    def y_setter(self, value):
        self.rb.setY(value)

    def z_getter(self):
        return self.rb.getZ()
    def z_setter(self, value):
        self.rb.setZ(value)

    def rotation_getter(self):
        rotation = self.rb.getHpr()
        return Vec3(rotation[1], rotation[0], rotation[2])
    def rotation_setter(self, value):
        self.rb.setHpr(Vec3(-value[1], -value[0], value[2]))

    def quaternion_getter(self):
        return self.rb.getQuat()
    def quaternion_setter(self, value):
        self.rb.setQuat(value)

    def rotation_x_setter(self, value):
        new_value = self.rotation
        new_value[0] = value
        self.rotation = new_value
    def rotation_y_getter(self):
        return self.rotation.y
    def rotation_y_setter(self, value):
        new_value = self.rotation
        new_value[1] = value
        self.rotation = new_value
    def rotation_z_setter(self, value):
        new_value = self.rotation
        new_value[2] = value
        self.rotation = new_value

    def scale_getter(self):
        scale = self.rb.getScale()
        return Vec3(scale[0], scale[1], scale[2])

    def scale_setter(self, value):
        if not isinstance(value, Vec2 | Vec3):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.scale[2])
        value = [e if e!=0 else .001 for e in value]
        self.rb.setScale(value[0], value[1], value[2])

    def world_scale_getter(self):
        scale = self.rb.getScale(scene)
        return Vec3(scale[0], scale[1], scale[2])

    def world_scale_setter(self, value):
        if not isinstance(value, Vec2 | Vec3):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.scale[2])
        value = [e if e!=0 else .001 for e in value]
        self.rb.setScale(scene, (value[0], value[1], value[2]))

    def color_getter(self):
        return self.entity.color
    def color_setter(self, value):
        self.entity.color = value

    def alpha_getter(self):
        return self.entity.alpha
    def alpha_setter(self, value):
        self.entity.alpha = value

    def texture_getter(self):
        return self.entity.texture
    def texture_setter(self, value):
        self.entity.texture = value

    def scale_y_getter(self): return self.scale.y
    def scale_y_setter(self, value):
        self.scale = Vec3(self.scale.x, value, self.scale.z)


    def mass_getter(self):
        return self.node.getMass()
    def mass_setter(self, value):
        self.node.setMass(value)

    def friction_getter(self):
        return self.node.getFriction()
    def friction_setter(self, value):
        self.node.setFriction(value)

    def rotational_friction_setter(self, value):
        self.node.setAngularDamping(value)

    def lock_axis_setter(self, value:Vec3):
        self._lock_axis = value
        self.node.setLinearFactor(Vec3(*[1-e for e in value]))

    def lock_rotation_setter(self, value:Vec3):
        self._lock_rotation = value
        self.node.setAngularFactor(Vec3(*[1-e for e in value]))


    def velocity_getter(self):
        return self.node.getLinearVelocity()
    def velocity_setter(self, value):
        return self.node.setLinearVelocity(value)

    def add_force(self, force, point=(0,0,0)):
        self.node.setActive(True)
        if point != (0,0,0):
            self.node.applyForce(force, point)
        else:
            self.node.applyCentralForce(force)

    def apply_impulse(self, force, point=(0,0,0)):
        self.node.setActive(True)
        if point != (0,0,0):
            self.node.applyImpulse(force, point)
        else:
            self.node.applyCentralImpulse(force)


    def collider_setter(self, value):   # set to 'box'/'sphere'/'capsule'/'mesh' for auto fitted collider.
        # print('set rb colliderto:', value)
        if value is None and self.collider:
            self.rb.node.removeShape(value)
            self._collider = None
            # self.collision = False
            return
        self._collider = None
        # destroy existing collider
        if value and self.collider:
            self.rb.node.removeShape(value)

        if isinstance(value, BulletPlaneShape | BulletBoxShape | BulletSphereShape | BulletCylinderShape | BulletCapsuleShape | BulletConeShape | BulletTriangleMeshShape):
            self._collider = value

        if isinstance(value, str) and value not in ('box', 'sphere', 'capsule', 'mesh'):
            raise ValueError(f"Incorrect value for auto-fitted collider: {value}. Choose one of: 'box', 'sphere', 'capsule', 'mesh'")

        elif value == 'box' or value == 'plane':
            if self.entity.model:
                _bounds = self.entity.model_bounds
                self._collider = BoxCollider(center=_bounds.center-(_bounds.size*self.entity.origin), size=_bounds.size)
            else:
                self._collider = BoxCollider()

        elif value == 'mesh':
            self._collider = MeshCollider(self.entity.model)

        elif value == 'sphere':
            _bounds = self.entity.model_bounds
            self._collider = SphereCollider(center=_bounds.center-(_bounds.size), radius=_bounds.size.x/2)

        if self._collider:
            self.node.addShape(self._collider)

        return

    def kinematic_setter(self, value):
        self._kinematic = value
        self.node.setKinematic(value)

    def enabled_getter(self):
        return getattr(self, '_enabled', True)
    def enabled_setter(self, value):
        self._enabled = value
        if hasattr(self, 'entity'):
            self.entity.enabled = value
        if hasattr(self, 'rb') and hasattr(self, 'world'):
            if value:
                self.world.attachRigidBody(self.node)
            else:
                self.world.removeRigidBody(self.node)


    # def intersects(self, other):
    #     result = self.world.contactTest(self.node)

    #     if not result.getNumContacts():
    #         return HitInfo()

    #     for i in range(result.getNumContacts()):
    #         contact = result.getContact(i)
    #         node0 = contact.getNode0()
    #         node1 = contact.getNode1()
    #         if node



if __name__ == '__main__':
    from ursina import Ursina, Cylinder, Capsule, Cone, Sequence, Func, curve, Wait, EditorCamera
    from ursina.physics import *

    app = Ursina(borderless=False)

    from ursina import *
    from ursina.physics import raycast, CapsuleCollider, BoxCollider, MeshCollider
    # Entity = PhysicsEntity

    class Player(PhysicsEntity):
        def __init__(self, **kwargs):
            super().__init__(collider=CapsuleCollider(), model=Capsule(), color=color.orange, y=2, z=0, mass=1, friction=1, lock_axis=Vec3(0,0,0), lock_rotation=Vec3(1,1,1), rotational_friction=Vec3.zero)
            Entity(parent=self, model='sphere', z=.2, y=.25, scale=1, color=color.red)

            self.camera_controller = EditorCamera(pan_speed=Vec2.zero)

            self.rotation_helper = Entity(loose_parent=self, model='wireframe_cube', visible=False)
            def rotation_helper_update():
                # print(self.position)
                self.rotation_helper.position = self.position
                self.rotation_helper.rotation_y = self.camera_controller.rotation_y
            self.rotation_helper.update = rotation_helper_update

            self.direction_helper = Entity(parent=self.rotation_helper, scale=.2, model='sphere', always_on_top=True, enabled=1, color=color.pink, visible=False)
            self.helper = Entity(parent=self)
            for key, value in kwargs.items():
                setattr(self, key, value)

            self.physics_update_loop = Sequence(self.physics_update, 1/30, loop=True, started=True)


        def update(self):
            self.camera_controller.position = lerp_exponential_decay(self.camera_controller.position, self.position, time.dt*10)


        def physics_update(self):
            h = max((held_keys['gamepad left stick x'], held_keys['d']-held_keys['a']), key=lambda x: abs(x))
            v = max((held_keys['gamepad left stick y'], held_keys['w']-held_keys['s']), key=lambda x: abs(x))
            direction = Vec3(h,0,v).normalized()
            limit = 14
            self.friction = 10 if direction.length() <.1 else .5

            self.input_strength = min(Vec3(h,0,v).length(), 1)
            if self.input_strength:
                self.direction_helper.position = direction * 3
                self.helper.look_at_2d(self.direction_helper.world_position, 'y')

                vel = self.velocity
                xz_vel = (self.helper.forward * 100 * self.input_strength).xz
                speed = xz_vel.length()
                if speed > limit:
                    xz_vel.normalize()
                    xz_vel *= limit
                vel.x = xz_vel.x
                vel.z = xz_vel.y
                self.velocity = vel

            self.grounded = raycast(self.position+(Vec3.down*.9), Vec3.down, distance=.2).hit
            self.color = color.orange if self.grounded else color.azure
            if not self.grounded:   # prevent sticking to walls
                self.friction = 0

        def input(self, key):
            if key in 'wasd ':
                self.physics_update()
            if key == 'space':
                print('jump')
                self.velocity = Vec3.zero
                self.apply_impulse(Vec3.up * 18)


    from ursina import Entity
    # EditorCamera()

    player = Player(x=10, z=-10)

    Entity = PhysicsEntity
    # Entity(model='cube', color=color.red, collider='box', mass=1)

    ground = Entity(model='cube', origin_y=.5, texture='grass', scale=Vec3(30,1,30), collider='box')
    cube = Entity(model='cube', texture='white_cube', x=2, y=3, collider='box', color=color.lime, mass=0)
    cube_with_origin = Entity(model='icosphere', origin=(0,-.5,0), scale=2, x=-1, y=3, z=-3, collider='sphere', color=color.orange, mass=0)

    slope = Entity(model='plane', collider='box', scale=10, x=-8, z=10, rotation_x=-30, y=2, color=color.red)

    icosphere = Entity(model='icosphere', collider='mesh', scale=4, x=10, z=0, y=2, color=color.violet)
    icosphere_2 = Entity(model='icosphere', collider='mesh', scale=.5, color=color.green)

    e = Entity(z=-2)
    sphere = Entity(parent=e, model='icosphere', collider='sphere', x=-4, scale=3, color=color.blue, )
    ground = Entity(model='cube', scale=10, collider='box', x=-8, z=-10, rotation_x=-10, y=-5, color=color.gray, name='ground')

    camera.fov = 100

    mover = Entity(model='cube', color=color.red)
    child = Entity(parent=mover, model='cube', origin_y=-.5, scale=2, collider='box', color=color.pink, x=-1)

    def input(key):
        if key == 't':
            sphere.enabled = not sphere.enabled

        if key == 'w':
            mover.z += 1
            # sphere.rb.enabled = not sphere.rb.enabled
            # sphere.rb.rigid_body_node.setActive(False)

        if key == 'c':
            for e in scene.entities:
                if e == player or e.parent==player:
                    continue

                if isinstance(e, PhysicsEntity):
                    destroy(e)
                    # physics_handler.world.remove(e.node)
                    # e.rb.removeNode()

                    # self.world.removeRigidBody(self.node)
                    # self.rb.removeNode()


    physics_handler.gravity = 50
    physics_handler.show_debug = True
    print('----------------------------', physics_handler.show_debug)

    app.run()
