import sys

from ursina import *
from ursina.entity import Entity
from ursina.mesh import Mesh
from ursina import scene
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue
from panda3d.core import CollisionRay, CollisionSegment, CollisionBox
from ursina.vec3 import Vec3
from math import sqrt, inf
from ursina.hit_info import HitInfo


class Raycaster(Entity):
    line_model = Mesh(vertices=[Vec3(0,0,0), Vec3(0,0,1)], mode='line')


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


    def raycast(self, origin, direction=(0,0,1), distance=inf, traverse_target=scene, ignore=list(), debug=False):
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

        ignore += tuple([e for e in scene.entities if not e.collision])

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
                # print('cast nP to Entity')
                self.hit.entity = e

        self.hit.point = point
        self.hit.world_point = world_point
        self.hit.distance = hit_dist

        self.hit.normal = Vec3(*self.collision.get_surface_normal(self.collision.get_into_node_path().parent).normalized())
        self.hit.world_normal = Vec3(*self.collision.get_surface_normal(render).normalized())
        return self.hit

        self.hit = HitInfo(hit=False, distance=distance)
        return self.hit


    def boxcast(self, origin, direction=(0,0,1), distance=9999, thickness=(1,1), traverse_target=scene, ignore=list(), debug=False):
        if isinstance(thickness, (int, float, complex)):
            thickness = (thickness, thickness)

        temp = Entity(
            position=origin,
            model='cube',
            origin_z=-.5,
            scale=Vec3(abs(thickness[0]), abs(thickness[1]), abs(distance)),
            collider='box',
            color=color.white33,
            always_on_top=debug,
            visible=debug
            )
        temp.look_at(origin + direction)
        hit_info = temp.intersects(traverse_target=traverse_target, ignore=ignore)
        if hit_info.world_point:
            hit_info.distance = ursinamath.distance(origin, hit_info.world_point)
        else:
            hit_info.distance = distance

        if debug:
            temp.collision = False
            temp.scale_z = hit_info.distance
            destroy(temp, delay=.2)
        else:
            destroy(temp)

        return hit_info


sys.modules[__name__] = Raycaster()




if __name__ == '__main__':
    app = Ursina()
    from ursina.entity import Entity

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
