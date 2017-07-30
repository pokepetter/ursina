from panda3d.core import *
import sys
import camera
import scene


class Mouse():


    def __init__(self):
        self.mouse_watcher = None
        self.position = (0,0)
        self.x = 0
        self.z = 0
        self.delta = (0,0)

        self.hovered_entity = None
        self.mouse_pressed = False
        self.result = None

    def input(self, key):
        if key.endswith('mouse down'):
            self.start_x = self.x
            self.start_z = self.z
            self.mouse_pressed = True
            print(self.result.hasHit())
        elif key.endswith('mouse up'):
            self.mouse_pressed = False


    def update(self, dt):
        if self.mouse_watcher.hasMouse():
            self.x = self.mouse_watcher.getMouseX()
            self.z = self.mouse_watcher.getMouseY()
            self.position = (self.x, self.z)

            pFrom = Point3()
            pTo = Point3()
            camera.lens.extrude(self.position, pFrom, pTo)
            # Transform to global coordinates
            pFrom = render.getRelativePoint(camera.cam, pFrom)
            pTo = render.getRelativePoint(camera.cam, pTo)

            self.result = scene.world.rayTestClosest(pFrom, pTo)

            # print(result.hasHit())
            # print result.getHitPos()
            # print result.getHitNormal()
            # print result.getHitFraction()
            # print result.getNode()



            if self.mouse_pressed:
                self.delta = (self.x - self.start_x, self.z - self.start_z)


sys.modules[__name__] = Mouse()
