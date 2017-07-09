from panda3d.core import *
import camera
import collision

global position
global x
global z
hovered_thing = None


def input(key):
    for thing in parent.things:
        if thing.enabled:
            for script in thing.scripts:
                try:
                    script.input(key)
                except:
                    pass

def update(dt):
    if mouse_watcher.hasMouse():
        global x
        x = mouse_watcher.getMouseX()
        global z
        z = mouse_watcher.getMouseY()
        global position
        position = (x,z)

        # pos3d = Point3()
        # nearPoint = Point3()
        # farPoint = Point3()
        # camera.lens.extrude(position, nearPoint, farPoint)
        # screen_depth = int(farPoint[1] - nearPoint[1])
        # collided = False
        # for i in range(screen_depth):
        #     if collided:
        #         break
        #     pos = nearPoint + (farPoint * i / screen_depth)
        #     for thing in parent.things:
        #         if thing.enabled and thing.collider:
        #             print(collision.point_inside_thing(pos, thing))
        #             collided = True
        #             break
