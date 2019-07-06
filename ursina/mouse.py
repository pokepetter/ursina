from panda3d.core import *
import sys
import time
import math
from ursina import camera
from ursina import scene
from ursina import application
from ursina import window
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from ursina.hit import Hit


class Mouse():

    def __init__(self):
        self.enabled = False
        self.locked = False
        self.position = Vec3(0,0,0)
        self.delta = Vec3(0,0,0)
        self.prev_x = 0
        self.prev_y = 0
        self.velocity = Vec3(0,0,0)
        self.prev_click_time = time.time()
        self.double_click_distance = .5

        self.hovered_entity = None
        self.left = False
        self.right = False
        self.middle = False
        self.delta_drag = Vec3(0,0,0)

        self.i = 0
        self.update_rate = 10
        self._mouse_watcher = None
        self._picker = CollisionTraverser()  # Make a traverser
        self._pq = CollisionHandlerQueue()  # Make a handler
        self._pickerNode = CollisionNode('mouseRay')
        self._pickerNP = camera.attach_new_node(self._pickerNode)
        self._pickerRay = CollisionRay()  # Make our ray
        self._pickerNode.addSolid(self._pickerRay)
        self._picker.addCollider(self._pickerNP, self._pq)
        self.raycast = True
        self.collision = None
        self.enabled = True

    @property
    def x(self):
        if not self._mouse_watcher.has_mouse():
            return 0
        return self._mouse_watcher.getMouseX() / 2 * window.aspect_ratio  # same space as ui stuff

    @property
    def y(self):
        if not self._mouse_watcher.has_mouse():
            return 0
        return self._mouse_watcher.getMouseY() / 2


    def __setattr__(self, name, value):

        if name == 'visible':
            window.set_cursor_hidden(not value)
            application.base.win.requestProperties(window)

        if name == 'locked':
            try:
                object.__setattr__(self, name, value)
                window.set_cursor_hidden(value)
                application.base.win.requestProperties(window)
            except:
                pass

        try:
            super().__setattr__(name, value)
            # return
        except:
            pass


    def input(self, key):
        if not self.enabled:
            return

        if key.endswith('mouse down'):
            self.start_x = self.x
            self.start_y = self.y

        elif key.endswith('mouse up'):
            self.delta_drag = Vec3(
                self.x - self.start_x,
                self.y - self.start_y,
                0
                )


        if key == 'left mouse down':
            self.left = True
            if self.hovered_entity:
                if hasattr(self.hovered_entity, 'on_click'):
                    self.hovered_entity.on_click()
                for s in self.hovered_entity.scripts:
                    if hasattr(s, 'on_click'):
                        s.on_click()
            # double click
            if time.time() - self.prev_click_time <= self.double_click_distance:
                base.input('double click')

                if self.hovered_entity:
                    if hasattr(self.hovered_entity, 'on_double_click'):
                        self.hovered_entity.on_double_click()
                    for s in self.hovered_entity.scripts:
                        if hasattr(s, 'on_double_click'):
                            s.on_double_click()

            self.prev_click_time = time.time()


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



    def update(self):
        if not self.enabled or not self._mouse_watcher.has_mouse():
            self.velocity = Vec3(0,0,0)
            return

        self.position = Vec3(self.x, self.y, 0)
        self.moving = self.x + self.y != self.prev_x + self.prev_y

        if self.moving:
            if self.locked:
                self.velocity = self.position
                application.base.win.move_pointer(0, int(window.size[0] / 2), int(window.size[1] / 2))
            else:
                self.velocity = Vec3(self.x - self.prev_x, (self.y - self.prev_y) / window.aspect_ratio ,0)
        else:
            self.velocity = Vec3(0,0,0)

        if self.left or self.right or self.middle:
            self.delta = Vec3(self.x - self.start_x, self.y - self.start_y, 0)

        self.prev_x = self.x
        self.prev_y = self.y


        self.i += 1
        if self.i < self.update_rate:
            return
        # collide with ui
        self._pickerNP.reparent_to(scene.ui_camera)
        self._pickerRay.set_from_lens(camera._ui_lens_node, self.x * 2 / window.aspect_ratio, self.y * 2)
        self._picker.traverse(camera.ui)
        if self._pq.get_num_entries() > 0:
            # print('collided with ui', self._pq.getNumEntries())
            self.find_collision()
            return

        # collide with world
        self._pickerNP.reparent_to(camera)
        self._pickerRay.set_from_lens(scene.camera.lens_node, self.x * 2, self.y * 2)
        self._picker.traverse(base.render)
        if self._pq.get_num_entries() > 0:
            # print('collided with world', self._pq.getNumEntries())
            self.find_collision()
            return
        # else:
        #     print('mouse miss', base.render)

        # unhover all if it didn't hit anything
        for entity in scene.entities:
            if hasattr(entity, 'hovered') and entity.hovered:
                entity.hovered = False
                self.hovered_entity = None
                if hasattr(entity, 'on_mouse_exit'):
                    entity.on_mouse_exit()
                for s in entity.scripts:
                    if hasattr(s, 'on_mouse_exit'):
                        s.on_mouse_exit()

    @property
    def normal(self):
        if not self.collision:
            return None
        if not self.collision.has_surface_normal():
            print('no surface normal')
            return None
        n = self.collision.get_surface_normal(self.collision.get_into_node_path().parent)
        return (n[0], n[2], n[1])

    @property
    def world_normal(self):
        if not self.collision:
            return None
        if not self.collision.has_surface_normal():
            print('no surface normal')
            return None
        n = self.collision.get_surface_normal(render)
        return (n[0], n[2], n[1])

    @property
    def point(self):
        if self.hovered_entity:
            p = self.collision.getSurfacePoint(self.hovered_entity)
            return Point3(p[0], p[2], p[1])
        else:
            return None

    @property
    def world_point(self):
        if self.hovered_entity:
            p = self.collision.getSurfacePoint(render)
            return Point3(p[0], p[2], p[1])
        else:
            return None

    def find_collision(self):
        if not self.raycast:
            return
        self._pq.sortEntries()
        if len(self._pq.get_entries()) == 0:
            self.collision = None
            return

        self.collisions = list()
        for entry in self._pq.getEntries():
            # print(entry.getIntoNodePath().parent)
            for entity in scene.entities:
                if entry.getIntoNodePath().parent == entity:
                    if entity.collision:
                        self.collisions.append(Hit(
                            hit = entry.collided(),
                            entity = entity,
                            distance = 0,
                            point = entry.getSurfacePoint(entity),
                            world_point = entry.getSurfacePoint(scene),
                            normal = entry.getSurfaceNormal(entity),
                            world_normal = entry.getSurfaceNormal(scene),
                            ))
                        break

        self.collision = self._pq.getEntry(0)
        nP = self.collision.getIntoNodePath().parent

        for entity in scene.entities:
            if not hasattr(entity, 'collision') or not entity.collision or not entity.collider:
                continue
            # if hit entity is not hovered, call on_mouse_enter()
            if entity == nP:
                if not entity.hovered:
                    entity.hovered = True
                    self.hovered_entity = entity
                    # print(entity.name)
                    if hasattr(entity, 'on_mouse_enter'):
                        entity.on_mouse_enter()
                    for s in entity.scripts:
                        if hasattr(s, 'on_mouse_enter'):
                            s.on_mouse_enter()
            # unhover the rest
            else:
                if entity.hovered:
                    entity.hovered = False
                    if hasattr(entity, 'on_mouse_exit'):
                        entity.on_mouse_exit()
                    for s in entity.scripts:
                        if hasattr(s, 'on_mouse_exit'):
                            s.on_mouse_exit()




sys.modules[__name__] = Mouse()
