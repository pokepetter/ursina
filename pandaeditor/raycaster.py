import sys

from pandaeditor import *
from pandaeditor.entity import Entity
from pandaeditor import scene
# from pandaeditor import render
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import Vec3
import math


class Raycaster(Entity):

    def __init__(self):
        super().__init__()
        self.picker = CollisionTraverser()  # Make a traverser
        self.pq = CollisionHandlerQueue()  # Make a handler
        self.pickerNode = CollisionNode('raycaster')
        self.pickerNP = self.attach_new_node(self.pickerNode)
        self.collision_ray = CollisionRay()  # Make our ray
        self.pickerNode.addSolid(self.collision_ray)
        self.picker.addCollider(self.pickerNP, self.pq)

    def set_up(self):
        # make debug model
        self.debug_model = Entity('raycaster_debug_model')
        self.debug_model.parent = render
        self.debug_model.model = 'cube'
        self.debug_model.color = color.yellow
        self.debug_model.origin = (0, 0, -.5)
        self.debug_model.enabled = False


    def distance(self, a, b):
        return math.sqrt(sum( (a - b)**2 for a, b in zip(a, b)))


    def raycast(self, origin, direction, dist, traverse_target=None, debug=False):
        # for debug
        self.position = origin
        self.look_at(self.position + direction)

        self.collision_ray.set_origin(Vec3(self.position[0], self.position[2], self.position[1]))
        self.collision_ray.set_direction(Vec3(self.forward[0], self.forward[2], self.forward[1]))

        self.debug_model.enabled = debug
        if debug:
            self.debug_model.scale = (.1, .1, dist)

        if traverse_target is None:
            traverse_target = scene

        # print('traverse', traverse_target)
        self.picker.traverse(traverse_target)

        if self.pq.get_num_entries() > 0:
            print('hit')
            self.pq.sort_entries()
            self.collision = self.pq.get_entry(0)
            nP = self.collision.get_into_node_path().parent
            self.point = self.collision.get_surface_point(render)
            hit_dist = self.distance(self.collision_ray.get_origin(), self.point)
            print(self.collision_ray.get_origin(), dist)
            if nP.name.endswith('.egg'):
                nP = nP.parent
                return True, nP
        else:
            print('miss')
            self.point = None
            return False


sys.modules[__name__] = Raycaster()

class RaycasterTest(Entity):

    def __init__(self):
        super().__init__()

    def input(self, key):
        if key == 'r':
            if raycast((0,0,-2), (0,0,1), 5, render, debug=True):
                print('hit', raycaster.point)


if __name__ == '__main__':
    app = PandaEditor()

    d = Entity()
    d.model = 'cube'
    d.color = color.red
    d.scale *= .2
    camera.position = (15, 15, -15)
    camera.look_at(raycaster)

    e = Entity()
    e.position = (0, 0, 1)
    e.model = 'cube'
    e.color = color.lime
    e.collider = 'box'
    raycast((0,0,-2), (0,0,1), 5, render, debug=True)
    r = RaycasterTest()
    app.run()
