import sys

from ursina import *
from ursina.entity import Entity
from ursina import scene
# from ursina import render
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import Vec3
import math
from ursina.hit import Hit


class Raycaster(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'raycaster'
        self.eternal = True

        self.picker = CollisionTraverser()  # Make a traverser
        self.pq = CollisionHandlerQueue()  # Make a handler

        self.pickerNode = CollisionNode('raycaster')
        self.pickerNP = self.attach_new_node(self.pickerNode)

        self.collision_ray = CollisionRay()  # Make our ray
        self.pickerNode.addSolid(self.collision_ray)

        self.picker.addCollider(self.pickerNP, self.pq)
        self.pickerNP.show()


    def distance(self, a, b):
        return math.sqrt(sum( (a - b)**2 for a, b in zip(a, b)))


    def raycast(self, origin, direction, dist=math.inf, traverse_target=scene, ignore=list(), debug=False):
        self.position = origin
        self.look_at(self.position + direction)
        # need to do this for it to work for some reason
        self.collision_ray.set_origin(Vec3(0,0,0))
        self.collision_ray.set_direction(Vec3(0,1,0))

        if debug:
            self.pickerNP.show()
        else:
            self.pickerNP.hide()

        self.picker.traverse(traverse_target)

        if self.pq.get_num_entries() == 0:
            self.hit = Hit(hit=False)
            return self.hit

        self.pq.sort_entries()
        self.entries = [        # filter out ignored entities
            e for e in self.pq.getEntries()
            if e.get_into_node_path().parent not in ignore
            ]

        if len(self.entries) == 0:
            self.hit = Hit(hit=False)
            return self.hit

        self.collision = self.entries[0]
        nP = self.collision.get_into_node_path().parent
        point = self.collision.get_surface_point(render)
        point = Vec3(point[0], point[2], point[1])
        hit_dist = self.distance(self.world_position, point)
        if hit_dist <= dist:
            if nP.name.endswith('.egg'):
                nP = nP.parent

            self.hit = Hit(hit=True)
            for e in scene.entities:
                if e == nP:
                    # print('cast nP to Entity')
                    self.hit.entity = e

            self.hit.point = point
            self.hit.distance = hit_dist
            normal = self.collision.get_surface_normal(self.collision.get_into_node_path().parent)
            self.hit.normal = (normal[0], normal[2], normal[1])
            normal = self.collision.get_surface_normal(render)
            self.hit.world_normal = (normal[0], normal[2], normal[1])
            return self.hit

        self.hit = Hit(hit=False)
        return self.hit


sys.modules[__name__] = Raycaster()




if __name__ == '__main__':
    app = Ursina()
    from ursina.entity import Entity

    d = Entity(parent=scene, position=(0,0,2), model='cube', color=color.red, collider='box')
    e = Entity(model='cube', color=color.lime)

    camera.position = (0, 15, -15)
    camera.look_at(e)
    # camera.reparent_to(e)
    speed = .01
    rotation_speed = .1


    def update():
        e.position += e.forward * held_keys['w'] * speed
        e.position += e.left * held_keys['a'] * speed
        e.position += e.back * held_keys['s'] * speed
        e.position += e.right * held_keys['d'] * speed

        e.rotation_y -= held_keys['q'] * rotation_speed
        e.rotation_y += held_keys['e'] * rotation_speed

        raycast(e.world_position, e.forward, 3, render, debug=True)



    raycast((0,0,-2), (0,0,1), 5, render, debug=False)

    EditorCamera()
    app.run()
