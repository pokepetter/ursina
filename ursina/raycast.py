import builtins
from ursina.entity import Entity
from ursina.mesh import Mesh
from ursina.scene import instance as scene
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue, CollisionRay
from ursina.vec3 import Vec3
from copy import copy
from ursina.hit_info import HitInfo
from ursina import ursinamath, color
from ursina.destroy import destroy



_line_model = Mesh(vertices=[Vec3(0,0,0), Vec3(0,0,1)], mode='line')

_raycaster = Entity(add_to_scene_entities=False)
_raycaster._picker = CollisionTraverser()  # Make a traverser
_raycaster._pq = CollisionHandlerQueue()  # Make a handler
_raycaster._pickerNode = CollisionNode('_raycaster')
_raycaster._pickerNode.set_into_collide_mask(0)
_raycaster._pickerNP = _raycaster.attach_new_node(_raycaster._pickerNode)
_raycaster._picker.addCollider(_raycaster._pickerNP, _raycaster._pq)
_ray = CollisionRay()
_ray.setOrigin(Vec3(0,0,0))
_ray.setDirection(Vec3(0,0,1))
_raycaster._pickerNode.addSolid(_ray)


def raycast(origin, direction:Vec3=(0,0,1), distance=9999, traverse_target:Entity=scene, ignore:list=None, debug=False, color=color.white):
    if not ignore:
        ignore = []

    _raycaster.position = origin
    _raycaster.look_at(_raycaster.position + direction)

    if debug:
        temp = Entity(position=origin, model=copy(_line_model), scale=Vec3(1,1,min(distance,9999)), color=color, add_to_scene_entities=False)
        temp.look_at(_raycaster.position + direction)
        destroy(temp, 1/30)

    _raycaster._picker.traverse(traverse_target)      #HALF!

    if _raycaster._pq.get_num_entries() == 0:
        _raycaster.hit = HitInfo(hit=False, distance=distance)
        return _raycaster.hit


    _raycaster._pq.sort_entries()
    entries = _raycaster._pq.getEntries()
    entities = [e.get_into_node_path().parent for e in entries]

    entries = [        # filter out ignored entities
        e for i, e in enumerate(entries)
        if entities[i] in scene.collidables
        and entities[i] not in ignore
        and ursinamath.distance(_raycaster.world_position, e.get_surface_point(builtins.render)) <= distance
        ]

    if len(entries) == 0:
        return HitInfo(hit=False)

    _raycaster.collision = entries[0]
    nP = _raycaster.collision.get_into_node_path().parent
    point = Vec3(*_raycaster.collision.get_surface_point(nP))
    world_point = Vec3(*_raycaster.collision.get_surface_point(builtins.render))

    hit_info = HitInfo(hit=True)
    hit_info.entities = [e.get_into_node_path().parent.getPythonTag('Entity') for e in entries]
    hit_info.entity = hit_info.entities[0]

    hit_info.point = point
    hit_info.world_point = world_point
    hit_info.distance = ursinamath.distance(_raycaster.world_position, hit_info.world_point)

    hit_info.normal = Vec3(*_raycaster.collision.get_surface_normal(_raycaster.collision.get_into_node_path().parent).normalized())
    hit_info.world_normal = Vec3(*_raycaster.collision.get_surface_normal(builtins.render).normalized())

    return hit_info


if __name__ == '__main__':
    from ursina import *
    from ursina import Ursina, Entity, held_keys, time, duplicate, camera, EditorCamera
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
            else:
                print(hit_info.entity)

    Player(model='cube', origin_y=-.5, color=color.orange)
    wall_left = Entity(model='cube', collider='box', scale_y=3, origin_y=-.5, color=color.azure, x=-4)
    wall_right = duplicate(wall_left, x=4)
    camera.y = 2
    app.run()

    # # test
    # # breakpoint()
    # d = Entity(parent=scene, position=(0,0,2), model='cube', color=color.orange, collider='box', scale=2)
    # e = Entity(model='cube', color=color.lime)
    #
    # camera.position = (0, 15, -15)
    # camera.look_at(e)
    # # camera.reparent_to(e)
    # speed = .01
    # rotation_speed = 1
    # intersection_marker = Entity(model='cube', scale=.2, color=color.red)
    #
    # def update():
    #     e.position += e.forward * held_keys['w'] * speed
    #     e.position += e.left * held_keys['a'] * speed
    #     e.position += e.back * held_keys['s'] * speed
    #     e.position += e.right * held_keys['d'] * speed
    #
    #     e.rotation_y -= held_keys['q'] * rotation_speed
    #     e.rotation_y += held_keys['e'] * rotation_speed
    #
    #     ray = raycast(e.world_position, e.forward, 3, debug=True)
    #     # ray = raycast(e.world_position, e.forward, 3, debug=True)
    #     # ray = boxcast(e.world_position, e.right, 3, debug=True)
    #     # print(ray.distance, ray2.distance)
    #     intersection_marker.world_position = ray.world_point
    #     intersection_marker.visible = ray.hit
    #     if ray.hit:
    #         d.color = color.azure
    #     else:
    #         d.color = color.orange

    # ray = raycast(e.world_position, e.forward, 3, debug=True)

    EditorCamera()
    app.run()
