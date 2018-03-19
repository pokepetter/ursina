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
        super().__init__('raycaster')
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


    def raycast(self, origin, direction, dist=1000, traverse_target=None, debug=False):
        self.position = origin
        self.look_at(self.position + direction)
        # need to do this for it to work for some reason
        self.collision_ray.set_origin(Vec3(0,0,0))
        self.collision_ray.set_direction(Vec3(0,1,0))

        # print('np pos', self.pickerNP.get_pos(render))
        # print('self pos', self.world_position)
        # print('np rot:', (-self.pickerNP.getP(render), -self.pickerNP.getH(render), self.pickerNP.getR(render)))
        # print('self rot', self.rotation)
        if debug:
            self.pickerNP.show()
        else:
            self.pickerNP.hide()

        if traverse_target is None:
            traverse_target = scene

        self.picker.traverse(traverse_target)

        if self.pq.get_num_entries() > 0:
            self.pq.sort_entries()
            self.collision = self.pq.get_entry(0)
            nP = self.collision.get_into_node_path().parent
            self.point = self.collision.get_surface_point(render)
            self.point = Vec3(self.point[0], self.point[2], self.point[1])
            hit_dist = self.distance(self.world_position, self.point)
            if hit_dist <= dist:
                if nP.name.endswith('.egg'):
                    nP = nP.parent

                self.hit = Hit()
                self.hit.hit = True
                self.hit.entity = nP
                self.hit.distance = hit_dist
                self.hit.point = self.point
                return self.hit

            self.hit = Hit()
            return self.hit
        else:
            self.hit = Hit()
            return self.hit

class Hit():
    def __init__(self):
        self.hit = False
        self.entity = None
        self.distance = None
        self.point = None


sys.modules[__name__] = Raycaster()

class RaycasterTest(Entity):

    def __init__(self):
        super().__init__()
        d = Entity()
        d.parent = scene
        d.position = (0, 0, 2)
        d.model = 'cube'
        d.color = color.red
        d.collider = 'box'
        # d.scale *= .2

        camera.position = (0, 15, -15)
        camera.look_at(self)
        camera.reparent_to(self)

        # e = Entity()
        # e.position = (0, 0, 1)
        self.model = 'cube'
        self.color = color.lime

        self.speed = .01
        self.rotation_speed = .1
        # self.collider = 'box'


    def update(self, dt):
        self.position += self.forward * held_keys['w'] * self.speed
        self.position += self.left * held_keys['a'] * self.speed
        self.position += self.back * held_keys['s'] * self.speed
        self.position += self.right * held_keys['d'] * self.speed

        self.rotation_y -= held_keys['q'] * self.rotation_speed
        self.rotation_y += held_keys['e'] * self.rotation_speed

        raycast(self.world_position, self.forward, 3, render, debug=True)



if __name__ == '__main__':
    app = PandaEditor()



    from pandaeditor.entity import Entity
    raycast((0,0,-2), (0,0,1), 5, render, debug=False)
    r = RaycasterTest()

    cam = r.add_script('editor_camera')
    app.run()
