from panda3d.core import *
import sys
import time
from ursina.entity import Entity
from ursina import camera
from ursina import scene
from ursina import application
from ursina import window
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay


class Mouse(object):

    def __init__(self):
        self.enabled = False
        self.mouse_watcher = None
        self.locked = False
        self.position = Vec2(0,0)
        self.delta = (0,0)
        self.prev_x = 0
        self.prev_y = 0
        self.velocity = (0,0)
        self.prev_click_time = time.time()
        self.double_click_distance = .5

        self.hovered_entity = None
        self.left = False
        self.right = False
        self.middle = False
        self.delta_drag = (0,0)

        self.i = 0
        self.update_rate = 10
        self.picker = CollisionTraverser()  # Make a traverser
        self.pq = CollisionHandlerQueue()  # Make a handler
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attach_new_node(self.pickerNode)
        self.pickerRay = CollisionRay()  # Make our ray
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)
        self.raycast = True
        self.collision = None
        self.enabled = True

    @property
    def x(self):
        if not self.mouse_watcher.has_mouse():
            return 0
        return self.mouse_watcher.getMouseX() / 2   # same space as ui stuff

    @property
    def y(self):
        if not self.mouse_watcher.has_mouse():
            return 0
        return self.mouse_watcher.getMouseY() / 2


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
            self.delta_drag = (
                self.x - self.start_x,
                self.y - self.start_y
                )


        if key == 'left mouse down':
            self.left = True
            if self.hovered_entity:
                if hasattr(self.hovered_entity, 'on_click'):
                    self.hovered_entity.on_click()
                for s in self.hovered_entity.scripts:
                    if hasattr(s, 'on_click'):
                        s.on_click()
                    # try:
                        # s.on_click()
                    # except:
                    #     pass
            # double click
            if time.time() - self.prev_click_time <= self.double_click_distance:
                base.input('double click')
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
        self.i += 1
        if self.i < self.update_rate:
            return

        if not self.enabled or not self.mouse_watcher.has_mouse():
            self.velocity = (0,0)
            return

        self.position = Vec2(self.x, self.y)

        if self.locked:
            self.velocity = (self.x, self.y)
            application.base.win.move_pointer(0, round(window.size[0] / 2), round(window.size[1] / 2))
        else:
            self.velocity = (self.x - self.prev_x, (self.y - self.prev_y) / window.aspect_ratio)


        if self.left or self.right or self.middle:
            self.delta = (self.x - self.start_x, self.y - self.start_y)

        self.prev_x = self.x
        self.prev_y = self.y

        # collide with ui
        self.pickerNP.reparent_to(scene.ui_camera)
        self.pickerRay.set_from_lens(camera.ui_lens_node, self.x * 2, self.y * 2)
        self.picker.traverse(camera.ui)
        if self.pq.get_num_entries() > 0:
            # print('collided with ui', self.pq.getNumEntries())
            self.find_collision()
            return

        # collide with world
        self.pickerNP.reparent_to(camera)
        self.pickerRay.set_from_lens(scene.camera.lens_node, self.x * 2, self.y * 2)
        self.picker.traverse(base.render)
        if self.pq.get_num_entries() > 0:
            # print('collided with world', self.pq.getNumEntries())
            self.find_collision()
            return
        # else:
        #     print('mouse miss', base.render)

        # unhover all if it didn't hit anything
        for entity in scene.entities:
            if entity.hovered:
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
    def global_normal(self):
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

    def find_collision(self):
        if not self.raycast:
            return
        self.pq.sortEntries()
        if len(self.pq.get_entries()) == 0:
            self.collision = None
            return

        self.collisions = list()
        for entry in self.pq.getEntries():
            # print(entry.getIntoNodePath().parent)
            for entity in scene.entities:
                if entry.getIntoNodePath().parent == entity:
                    if entity.collision:
                        self.collisions.append(Collision(
                            entry.collided(),
                            entity,
                            entry.getSurfacePoint(entity),
                            entry.getSurfaceNormal(entity)
                            ))
                        break

        self.collision = self.pq.getEntry(0)
        nP = self.collision.getIntoNodePath().parent

        for entity in scene.entities:
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


class Collision(object):
    def __init__(self, collided, entity, position, normal):
        self.collided = collided
        self.entity = entity
        self.position = position
        self.normal = normal


sys.modules[__name__] = Mouse()
