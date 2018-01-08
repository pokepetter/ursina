import sys

from pandaeditor import *
from pandaeditor.entity import Entity
from pandaeditor import scene
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import Vec3

class Raycaster(Entity):

    def __init__(self):
        super().__init__()
        # self.parent = camera.render
        self.picker = CollisionTraverser()  # Make a traverser
        self.pq = CollisionHandlerQueue()  # Make a handler
        self.pickerNode = CollisionNode('raycaster')
        self.pickerNP = self.attach_new_node(self.pickerNode)
        self.collision_ray = CollisionRay()  # Make our ray
        self.pickerNode.addSolid(self.collision_ray)
        self.picker.addCollider(self.pickerNP, self.pq)





    def raycast(self, origin, direction, distance, traverse_target=scene.entity):
        # for debug
        self.position = origin
        self.look_at(self.position + Vec3(direction[0], direction[2], direction[1]))

        self.collision_ray.set_origin(Vec3(self.position[0], self.position[2], self.position[1]))
        self.collision_ray.set_direction(Vec3(self.forward[0], self.forward[2], self.forward[1]))

        self.parent = scene.render
        self.model = 'cube'
        self.color = color.yellow
        self.origin = (0, 0, -.5)

        self.scale = (.1, .1, distance)


        if traverse_target is None:
            print('traverse_target is None')
            return False

        self.picker.traverse(traverse_target)

        if self.pq.get_num_entries() > 0:
            self.pq.sort_entries()
            self.collision = self.pq.get_entry(0)
            nP = self.collision.get_into_node_path().parent
            point = self.collision.get_surface_point(scene.render)
            dist = distance(self.collision_ray.get_origin(), point)
            print(dist)
            if nP.name.endswith('.egg'):
                nP = nP.parent
                return nP
        else:
            return False


sys.modules[__name__] = Raycaster()

class RaycasterTest(Entity):

    def __init__(self):
        super().__init__()

    def input(self, key):
        if key == 'r':
            print('r')
            raycast((0,0,0), (0,0,1), 5, scene.render)

if __name__ == '__main__':
    app = PandaEditor()

    # raycaster.parent = scene.render
    # raycaster.model = 'cube'
    # raycaster.color = color.yellow
    # raycaster.origin = (0, 0, -.5)
    # raycaster.scale *= .1

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
    raycast((0,0,0), (0,0,1), 5, scene.entity)
    r = RaycasterTest()
    app.run()
