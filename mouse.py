from panda3d.core import *
import camera
import collision

global position
global x
global z
# parent
# mouse_watcher
global hovered_gameobject
hovered_gameobject = None


def input(key):
    for gameobject in parent.gameobjects:
        if gameobject.enabled:
            for script in gameobject.scripts:
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

        pos3d = Point3()
        nearPoint = Point3()
        farPoint = Point3()
        camera.lens.extrude(position, nearPoint, farPoint)
        screen_depth = int(farPoint[1] - nearPoint[1])
        collided = False
        for i in range(screen_depth):
            if collided:
                break
            pos = nearPoint + (farPoint * i / screen_depth)
            pos += camera.cam.getPos(parent.render) + pos
            for gameobject in parent.gameobjects:
                if gameobject.enabled and gameobject.collider:
                    if collision.point_inside_gameobject(pos, gameobject):
                        collided = True
                        global hovered_gameobject
                        hovered_gameobject = gameobject
                        if not gameobject.hovered:
                            gameobject.hovered = True
                            for script in hovered_gameobject.scripts:
                                try:
                                    script.on_mouse_enter()
                                except:
                                    pass
                        break
            # if it raycast the whole way through,
            if i == screen_depth-1:
                try:
                    if hovered_gameobject.hovered:
                        hovered_gameobject.hovered = False
                        for script in hovered_gameobject.scripts:
                            try:
                                script.on_mouse_exit()
                            except:
                                pass
                except:
                    pass


        for gameobject in parent.gameobjects:
            if (gameobject.enabled and gameobject.collision
            and gameobject.hovered and not gameobject == hovered_gameobject):
                gameobject.hovered = False
                for script in gameobject.scripts:
                    try:
                        script.on_mouse_exit()
                    except:
                        pass
