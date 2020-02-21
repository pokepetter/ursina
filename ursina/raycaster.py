import sys

from ursina import *
from ursina.entity import Entity
from ursina import scene
# from ursina import render
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue
from panda3d.core import CollisionRay, CollisionSegment, CollisionBox
from ursina.vec3 import Vec3
import math
from ursina.hit import Hit


class Raycaster(Entity):

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
        self._pickerNP.show()


    def distance(self, a, b):
        return math.sqrt(sum( (a - b)**2 for a, b in zip(a, b)))


    def raycast(self, origin, direction=(0,0,1), distance=math.inf, traverse_target=scene, ignore=list(), debug=False):
        self.position = origin
        self.look_at(self.position + direction)
        self._pickerNode.clearSolids()
        # if thickness == (0,0):
        if distance == math.inf:
            ray = CollisionRay()
            ray.setOrigin(Vec3(0,0,0))
            ray.setDirection(Vec3(0,1,0))
        else:
            ray = CollisionSegment(Vec3(0,0,0), Vec3(0,distance,0))

        self._pickerNode.addSolid(ray)


        if debug:
            self._pickerNP.show()
        else:
            self._pickerNP.hide()

        self._picker.traverse(traverse_target)

        if self._pq.get_num_entries() == 0:
            self.hit = Hit(hit=False)
            return self.hit

        ignore += tuple([e for e in scene.entities if not e.collision])

        self._pq.sort_entries()
        self.entries = [        # filter out ignored entities
            e for e in self._pq.getEntries()
            if e.get_into_node_path().parent not in ignore
            ]

        if len(self.entries) == 0:
            self.hit = Hit(hit=False)
            return self.hit

        self.collision = self.entries[0]
        nP = self.collision.get_into_node_path().parent
        point = self.collision.get_surface_point(nP)
        point = Vec3(point[0], point[2], point[1])
        world_point = self.collision.get_surface_point(render)
        world_point = Vec3(world_point[0], world_point[2], world_point[1])
        hit_dist = self.distance(self.world_position, world_point)

        if nP.name.endswith('.egg'):
            nP = nP.parent

        self.hit = Hit(hit=True)
        for e in scene.entities:
            if e == nP:
                # print('cast nP to Entity')
                self.hit.entity = e

        self.hit.point = point
        self.hit.world_point = world_point
        self.hit.distance = hit_dist

        normal = self.collision.get_surface_normal(self.collision.get_into_node_path().parent)
        self.hit.normal = (normal[0], normal[2], normal[1])

        normal = self.collision.get_surface_normal(render)
        self.hit.world_normal = (normal[0], normal[2], normal[1])
        return self.hit

        self.hit = Hit(hit=False)
        return self.hit


    def boxcast(self, origin, direction=(0,0,1), distance=math.inf, thickness=(1,1), traverse_target=scene, ignore=list(), debug=False):
        if isinstance(thickness, (int, float, complex)):
            thickness = (thickness, thickness)
        resolution = 3
        rays = list()
        debugs = list()

        for y in range(3):
            for x in range(3):
                pos = origin + Vec3(lerp(-(thickness[0]/2), thickness[0]/2, x/(3-1)), lerp(-(thickness[1]/2), thickness[1]/2, y/(3-1)), 0)
                ray = self.raycast(pos, direction, distance, traverse_target, ignore, False)
                rays.append(ray)

                if debug and ray.hit:
                    d = Entity(model='cube', origin_z=-.5, position=pos, scale=(.02, .02, distance), ignore=True)
                    d.look_at(pos + Vec3(direction))
                    debugs.append(d)
                    # print(pos, hit.point)
                    if ray.hit and ray.distance > 0:
                        d.scale_z = ray.distance
                        d.color = color.green

        from ursina import destroy
        # [destroy(e, 1/60) for e in debugs]

        rays.sort(key=lambda x : x.distance)
        closest = rays[0]

        return Hit(
            hit = sum([int(e.hit) for e in rays]) > 0,
            entity = closest.entity,
            point = closest.point,
            world_point = closest.world_point,
            distance = closest.distance,
            normal = closest.normal,
            world_normal = closest.world_normal,

            hits = [e.hit for e in rays],
            entities = list(set([e.entity for e in rays])), # get unique entities hit
            )

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
    rotation_speed = .1
    intersection_marker = Entity(model='cube', scale=.2, color=color.red)

    def update():
        e.position += e.forward * held_keys['w'] * speed
        e.position += e.left * held_keys['a'] * speed
        e.position += e.back * held_keys['s'] * speed
        e.position += e.right * held_keys['d'] * speed

        e.rotation_y -= held_keys['q'] * rotation_speed
        e.rotation_y += held_keys['e'] * rotation_speed

        # ray = raycast(e.world_position, e.forward, 3, debug=True)
        ray = boxcast(e.world_position, e.forward, 3, thickness=.3, debug=False)
        # print(ray.distance, ray2.distance)
        intersection_marker.world_position = ray.world_point
        intersection_marker.visible = ray.hit
        if ray.hit:
            d.color = color.azure
        else:
            d.color = color.orange

    t = time.time()
    ray = boxcast(e.world_position, e.forward, 3, thickness=.3, debug=False)
    print(time.time() - t)
    raycast((0,0,-2), (0,0,1), 5, debug=False)

    EditorCamera()
    app.run()
