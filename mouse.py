from panda3d.core import *
import sys
import camera
import scene
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay


class Mouse():


    def __init__(self):
        self.enabled = False
        self.mouse_watcher = None
        self.position = (0,0)
        self.x = 0
        self.z = 0
        self.delta = (0,0)

        self.hovered_entity = None
        self.left = False
        self.right = False
        self.middle = False

        self.picker = CollisionTraverser()  # Make a traverser
        self.pq = CollisionHandlerQueue()  # Make a handler
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerRay = CollisionRay()  # Make our ray
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)


    def input(self, key):
        if not self.enabled:
            return

        if key.endswith('mouse down'):
            self.start_x = self.x
            self.start_z = self.z
            # print('yay^^')

        if key == 'left mouse down':
            self.left = True
        if key == 'left mouse up':
            self.left = False
        if key == 'right mouse down':
            self.right = True
        if key == 'right mouse up':
            self.right = False
        if key == 'middle mouse down':
            self.middle = True
        if key == 'middle mouse up':
            self.middle = False


    def update(self, dt):
        if not self.enabled:
            return

        if self.mouse_watcher.hasMouse():
            self.x = self.mouse_watcher.getMouseX()
            self.z = self.mouse_watcher.getMouseY()
            self.position = (self.x, self.z)

            if self.left or self.right or self.middle:
                self.delta = (self.x - self.start_x, self.z - self.start_z)


            # collide with ui
            self.pickerNP.reparentTo(scene.ui_camera)
            self.pickerRay.setFromLens(camera.ui_lens_node, self.x, self.z)
            self.picker.traverse(scene.ui)
            if self.pq.getNumEntries() > 0:
                # print('collided with ui', self.pq.getNumEntries())
                self.find_collision()
                return

            # collide with world
            self.pickerNP.reparentTo(camera)
            self.pickerRay.setFromLens(scene.camera.lens_node, self.x, self.z)
            self.picker.traverse(scene.render)
            if self.pq.getNumEntries() > 0:
                # print('collided with world', self.pq.getNumEntries())
                self.find_collision()
                return

            # unhover all if it didn't hit anything
            for entity in scene.entities:
                if entity.hovered:
                    entity.hovered = False
                    self.hovered_entity = None
                    for s in entity.scripts:
                        try:
                            s.on_mouse_exit()
                        except:
                            pass


    def find_collision(self):
        self.pq.sortEntries()
        nP = self.pq.getEntry(0).getIntoNodePath().parent
        if nP.name.endswith('.egg'):
            nP = nP.parent

            for entity in scene.entities:
                # if hit entity is not hovered, call on_mouse_enter()
                if entity == nP:
                    if not entity.hovered:
                        entity.hovered = True
                        self.hovered_entity = entity
                        # print(entity.name)
                        for s in entity.scripts:
                            try:
                                s.on_mouse_enter()
                            except:
                                pass
                # unhover the rest
                else:
                    if entity.hovered:
                        entity.hovered = False
                        for s in entity.scripts:
                            try:
                                s.on_mouse_exit()
                            except:
                                pass






sys.modules[__name__] = Mouse()
