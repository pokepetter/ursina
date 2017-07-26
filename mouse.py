from panda3d.core import *
import sys
import camera
import collision
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


    def input(self, key):
        if key.endswith('mouse down'):
            self.start_x = self.x
            self.start_z = self.z
            self.mouse_pressed = True
        elif key.endswith('mouse up'):
            self.mouse_pressed = False


    def update(self, dt):
        if self.mouse_watcher.hasMouse():
            self.x = self.mouse_watcher.getMouseX()
            self.z = self.mouse_watcher.getMouseY()
            self.position = (self.x, self.z)

            pos3d = Point3()
            nearPoint = Point3()
            farPoint = Point3()
            camera.lens.extrude(self.position, nearPoint, farPoint)
            screen_depth = int(farPoint[1] - nearPoint[1])
            collided = False
            for i in range(screen_depth):
                if collided:
                    break
                pos = nearPoint + (farPoint * i / screen_depth)
                pos += camera.cam.getPos(scene.render) + pos
                for entity in scene.entities:
                    if entity.enabled and entity.collider:
                        if collision.point_inside_entity(pos, entity):
                            collided = True
                            self.hovered_entity = entity
                            if not entity.hovered:
                                entity.hovered = True
                                for script in self.hovered_entity.scripts:
                                    try:
                                        script.on_mouse_enter()
                                    except:
                                        pass
                            break

                # if it raycast the whole way through,
                if i == screen_depth-1:
                    try:
                        if self.hovered_entity.hovered:
                            self.hovered_entity.hovered = False
                            for script in self.hovered_entity.scripts:
                                try:
                                    script.on_mouse_exit()
                                except:
                                    pass
                    except:
                        pass


            for entity in scene.entities:
                if (entity.enabled and entity.collision
                and entity.hovered and not entity == self.hovered_entity):
                    entity.hovered = False
                    for script in entity.scripts:
                        try:
                            script.on_mouse_exit()
                        except:
                            pass

            if self.mouse_pressed:
                self.delta = (self.x - self.start_x, self.z - self.start_z)


sys.modules[__name__] = Mouse()
