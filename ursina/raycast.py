import sys

from ursina.entity import Entity
from ursina.mesh import Mesh
from ursina.scene import instance as scene
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue, CollisionRay
from ursina.vec3 import Vec3
from math import sqrt, inf
from ursina.hit_info import HitInfo
from ursina import ursinamath, color
from ursina.ursinastuff import destroy, invoke


_line_model = Mesh(vertices=[Vec3(0,0,0), Vec3(0,0,1)], mode='line')

_raycaster = Entity()
_raycaster._picker = CollisionTraverser()  # Make a traverser
_raycaster._pq = CollisionHandlerQueue()  # Make a handler
_raycaster._pickerNode = CollisionNode('_raycaster')
_raycaster._pickerNode.set_into_collide_mask(0)
_raycaster._pickerNP = _raycaster.attach_new_node(_raycaster._pickerNode)
_raycaster._picker.addCollider(_raycaster._pickerNP, _raycaster._pq)


def raycast(origin, direction=(0,0,1), distance=inf, traverse_target=scene, ignore=[], debug=False):
    _raycaster.position = origin
    _raycaster.look_at(_raycaster.position + direction)

    _raycaster._pickerNode.clearSolids()
    ray = CollisionRay()
    ray.setOrigin(Vec3(0,0,0))
    ray.setDirection(Vec3(0,0,1))

    _raycaster._pickerNode.addSolid(ray)

    if debug:
        temp = Entity(position=origin, model=_line_model, scale=Vec3(1,1,min(distance,9999)), add_to_scene_entities=False)
        temp.look_at(_raycaster.position + direction)
        destroy(temp, 1/30)

    _raycaster._picker.traverse(traverse_target)

    if _raycaster._pq.get_num_entries() == 0:
        _raycaster.hit = HitInfo(hit=False, distance=distance)
        return _raycaster.hit

    ignore += tuple(e for e in scene.entities if not e.collision)

    _raycaster._pq.sort_entries()
    _raycaster.entries = [        # filter out ignored entities
        e for e in _raycaster._pq.getEntries()
        if e.get_into_node_path().parent not in ignore
        and ursinamath.distance(_raycaster.world_position, Vec3(*e.get_surface_point(render))) <= distance
        ]

    if len(_raycaster.entries) == 0:
        _raycaster.hit = HitInfo(hit=False, distance=distance)
        return _raycaster.hit

    _raycaster.collision = _raycaster.entries[0]
    nP = _raycaster.collision.get_into_node_path().parent
    point = Vec3(*_raycaster.collision.get_surface_point(nP))
    world_point = Vec3(*_raycaster.collision.get_surface_point(render))
    hit_dist = ursinamath.distance(_raycaster.world_position, world_point)


    _raycaster.hit = HitInfo(hit=True, distance=distance)
    for e in scene.entities:
        if e == nP:
            _raycaster.hit.entity = e

    nPs = [e.get_into_node_path().parent for e in _raycaster.entries]
    _raycaster.hit.entities = [e for e in scene.entities if e in nPs]

    _raycaster.hit.point = point
    _raycaster.hit.world_point = world_point
    _raycaster.hit.distance = hit_dist

    _raycaster.hit.normal = Vec3(*_raycaster.collision.get_surface_normal(_raycaster.collision.get_into_node_path().parent).normalized())
    _raycaster.hit.world_normal = Vec3(*_raycaster.collision.get_surface_normal(render).normalized())
    return _raycaster.hit

    _raycaster.hit = HitInfo(hit=False, distance=distance)
    return _raycaster.hit


if __name__ == '__main__':
    from ursina import *
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
