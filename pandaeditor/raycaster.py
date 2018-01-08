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
        self.pickerRay = CollisionRay()  # Make our ray
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)



    def raycast(self, origin, direction, distance, target=scene.entity):
        # collide with world
        # self.pickerNP.reparent_to(target)
        # self.pickerRay.set_from_lens(scene.camera.lens_node, self.x, self.y)
        # self.picker.traverse(scene.render)
        # if self.pq.get_num_entries() > 0:
        #     print('get_num_entries:', self.pq.getNumEntries())
        #     # self.find_collision()
        #     return

        self.world_position = origin
        self.look_at(self.position + Vec3(direction[0], direction[2], direction[1]))
        self.scale = (.1, .1, distance)
        

        if target is None:
            print('target is None')
            return

        print('traversing:', target)


        self.picker.traverse(target)

        if self.pq.get_num_entries() > 0:
            print('get_num_entries:', self.pq.getNumEntries())
        else:
            print('miss')


sys.modules[__name__] = Raycaster()

class RaycasterTest(Entity):

    def __init__(self):
        super().__init__()

    def input(self, key):
        if key == 'r':
            print('r')
            raycast((0,0,0), (0,0,1), 5, scene.entity)

if __name__ == '__main__':
    app = PandaEditor()

    raycaster.parent = scene.render
    raycaster.model = 'cube'
    raycaster.color = color.yellow
    raycaster.origin = (0, 0, -.5)
    raycaster.scale *= .1

    d = Entity()
    d.model = 'cube'
    d.color = color.red
    d.scale *= .2
    camera.position = (15, 15, -15)
    camera.look_at(raycaster)

    e = Entity()
    e.z = 1
    e.model = 'cube'
    e.color = color.lime
    e.collider = 'box'
    raycast((0,0,0), (0,0,1), 5, scene.entity)
    r = RaycasterTest()
    app.run()
