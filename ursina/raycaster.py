import sys

from ursina import *
from ursina.entity import Entity
from ursina.mesh import Mesh
from ursina.scene import instance as scene
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue
from panda3d.core import CollisionRay, CollisionSegment, CollisionBox
from ursina.vec3 import Vec3
from math import sqrt, inf
from ursina.hit_info import HitInfo


class Raycaster(Entity):
    line_model = Mesh(vertices=[Vec3(0,0,0), Vec3(0,0,1)], mode='line')
    _boxcast_box = Entity(model='cube', origin_z=-.5, collider='box', color=color.white33, enabled=False, eternal=True)

    def __init__(self):
        super().__init__(
            name = 'raycaster',
            eternal = True
            )
        self._picker = CollisionTraverser()  # Make a traverser
        self._pq = CollisionHandlerQueue()  # Make a handler
        self._pickerNode = CollisionNode('raycaster')
        self._pickerNode.set_into_collide_mask(0)
        self._pickerNP = self.attach_new_node(self._pickerNode)
        self._picker.addCollider(self._pickerNP, self._pq)


    def distance(self, a, b):
        return sqrt(sum( (a - b)**2 for a, b in zip(a, b)))


    def raycast(self, origin, direction=(0,0,1), distance=inf, traverse_target=scene, ignore=[], debug=False):
        self.position = origin
        self.look_at(self.position + direction)

        self._pickerNode.clearSolids()
        ray = CollisionRay()
        ray.setOrigin(Vec3(0,0,0))
        ray.setDirection(Vec3(0,0,1))

        self._pickerNode.addSolid(ray)

        if debug:
            temp = Entity(position=origin, model=Raycaster.line_model, scale=Vec3(1,1,min(distance,9999)), add_to_scene_entities=False)
            temp.look_at(self.position + direction)
            destroy(temp, 1/30)

        self._picker.traverse(traverse_target)

        if self._pq.get_num_entries() == 0:
            self.hit = HitInfo(hit=False, distance=distance)
            return self.hit

        ignore += tuple(e for e in scene.entities if not e.collision)

        self._pq.sort_entries()
        self.entries = [        # filter out ignored entities
            e for e in self._pq.getEntries()
            if e.get_into_node_path().parent not in ignore
            and self.distance(self.world_position, Vec3(*e.get_surface_point(render))) <= distance
            ]

        if len(self.entries) == 0:
            self.hit = HitInfo(hit=False, distance=distance)
            return self.hit

        self.collision = self.entries[0]
        nP = self.collision.get_into_node_path().parent
        point = Vec3(*self.collision.get_surface_point(nP))
        world_point = Vec3(*self.collision.get_surface_point(render))
        hit_dist = self.distance(self.world_position, world_point)


        self.hit = HitInfo(hit=True, distance=distance)
        for e in scene.entities:
            if e == nP:
                self.hit.entity = e

        nPs = [e.get_into_node_path().parent for e in self.entries]
        self.hit.entities = [e for e in scene.entities if e in nPs]

        self.hit.point = point
        self.hit.world_point = world_point
        self.hit.distance = hit_dist

        self.hit.normal = Vec3(*self.collision.get_surface_normal(self.collision.get_into_node_path().parent).normalized())
        self.hit.world_normal = Vec3(*self.collision.get_surface_normal(render).normalized())
        return self.hit

        self.hit = HitInfo(hit=False, distance=distance)
        return self.hit


    def boxcast(self, origin, direction=(0,0,1), distance=9999, thickness=(1,1), traverse_target=scene, ignore=[], debug=False): # similar to raycast, but with width and height
        if isinstance(thickness, (int, float, complex)):
            thickness = (thickness, thickness)

        Raycaster._boxcast_box.enabled = True
        Raycaster._boxcast_box.collision = True
        Raycaster._boxcast_box.position = origin
        Raycaster._boxcast_box.scale = Vec3(abs(thickness[0]), abs(thickness[1]), abs(distance))
        Raycaster._boxcast_box.always_on_top = debug
        Raycaster._boxcast_box.visible = debug

        Raycaster._boxcast_box.look_at(origin + direction)
        hit_info = Raycaster._boxcast_box.intersects(traverse_target=traverse_target, ignore=ignore)
        if hit_info.world_point:
            hit_info.distance = ursinamath.distance(origin, hit_info.world_point)
        else:
            hit_info.distance = distance

        if debug:
            Raycaster._boxcast_box.collision = False
            Raycaster._boxcast_box.scale_z = hit_info.distance
            invoke(setattr, Raycaster._boxcast_box, 'enabled', False, delay=.2)
        else:
            Raycaster._boxcast_box.enabled = False

        return hit_info


instance = Raycaster()
sys.modules[__name__] = instance




if __name__ == '__main__':
    app = Ursina()

    '''
    Casts a ray from *origin*, in *direction*, with length *distance* and returns
    a HitInfo containing information about what it hit. This ray will only hit entities with a collider.

    Use optional *traverse_target* to only be able to hit a specific entity and its children/descendants.
    Use optional *ignore* list to ignore certain entities.
    Setting debug to True will draw the line on screen.

    Example where we only move if a wall is not hit:
    '''


    class Player(Entity):

        def update(self):
            self.direction = Vec3(
                self.forward * (held_keys['w'] - held_keys['s'])
                + self.right * (held_keys['d'] - held_keys['a'])
                ).normalized()  # get the direction we're trying to walk in.

            origin = self.world_position + (self.up*.5) # the ray should start slightly up from the ground so we can walk up slopes or walk over small objects.
            hit_info = raycast(origin , self.direction, ignore=(self,), distance=.5, debug=False)
            if not hit_info.hit:
                self.position += self.direction * 5 * time.dt

    Player(model='cube', origin_y=-.5, color=color.orange)
    wall_left = Entity(model='cube', collider='box', scale_y=3, origin_y=-.5, color=color.azure, x=-4)
    wall_right = duplicate(wall_left, x=4)
    camera.y = 2
    app.run()

    # test
    breakpoint()
    d = Entity(parent=scene, position=(0,0,2), model='cube', color=color.orange, collider='box', scale=2)
    e = Entity(model='cube', color=color.lime)

    camera.position = (0, 15, -15)
    camera.look_at(e)
    # camera.reparent_to(e)
    speed = .01
    rotation_speed = 1
    intersection_marker = Entity(model='cube', scale=.2, color=color.red)

    def update():
        e.position += e.forward * held_keys['w'] * speed
        e.position += e.left * held_keys['a'] * speed
        e.position += e.back * held_keys['s'] * speed
        e.position += e.right * held_keys['d'] * speed

        e.rotation_y -= held_keys['q'] * rotation_speed
        e.rotation_y += held_keys['e'] * rotation_speed

        # ray = raycast(e.world_position, e.forward, 3, debug=True)
        # ray = raycast(e.world_position, e.forward, 3, debug=True)
        ray = boxcast(e.world_position, e.right, 3, debug=True)
        # print(ray.distance, ray2.distance)
        intersection_marker.world_position = ray.world_point
        intersection_marker.visible = ray.hit
        if ray.hit:
            d.color = color.azure
        else:
            d.color = color.orange

    t = time.time()
    # ray = raycast(e.world_position, e.forward, 3, debug=True)
    print(time.time() - t)
    # raycast((0,0,-2), (0,0,1), 5, debug=False)

    EditorCamera()
    app.run()
