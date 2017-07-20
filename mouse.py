from panda3d.core import *
import camera
import collision
import scene

global position
global x
global z
# parent
# mouse_watcher
global hovered_entity
hovered_entity = None


def input(key):
    for entity in scene.entities:
        if entity.enabled:
            for script in entity.scripts:
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
            for entity in scene.entities:
                if entity.enabled and entity.collider:
                    if collision.point_inside_entity(pos, entity):
                        collided = True
                        global hovered_entity
                        hovered_entity = entity
                        if not entity.hovered:
                            entity.hovered = True
                            for script in hovered_entity.scripts:
                                try:
                                    script.on_mouse_enter()
                                except:
                                    pass
                        break
            # if it raycast the whole way through,
            if i == screen_depth-1:
                try:
                    if hovered_entity.hovered:
                        hovered_entity.hovered = False
                        for script in hovered_entity.scripts:
                            try:
                                script.on_mouse_exit()
                            except:
                                pass
                except:
                    pass


        for entity in scene.entities:
            if (entity.enabled and entity.collision
            and entity.hovered and not entity == hovered_entity):
                entity.hovered = False
                for script in entity.scripts:
                    try:
                        script.on_mouse_exit()
                    except:
                        pass
