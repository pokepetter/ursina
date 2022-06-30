import sys
import time
import traceback
from panda3d.core import *
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from ursina import application
from ursina.window import instance as window
from ursina.scene import instance as scene
from ursina.camera import instance as camera
from ursina.hit_info import HitInfo
from ursina.ursinamath import distance


class Mouse():

    def __init__(self):
        self.enabled = False
        self.visible = True
        self.locked = False
        self.position = Vec3(0,0,0)
        self.delta = Vec3(0,0,0)    # movement since you pressed a mouse button.
        self.prev_x = 0
        self.prev_y = 0
        self.start_x = 0
        self.start_y = 0
        self.velocity = Vec3(0,0,0)
        self.moving = False
        self.prev_click_time = time.time()
        self.prev_click_pos = None
        self.double_click_distance = .5
        self.double_click_movement_limit = .01

        self.hovered_entity = None # returns the closest hovered entity with a collider.
        self.left = False
        self.right = False
        self.middle = False
        self.delta_drag = Vec3(0,0,0)   # movement between left mouse down and left mouse up.

        self.update_step = 1
        self.traverse_target = scene  # set this to None to disable collision with scene, which might be a good idea if you have lots of colliders.
        self._i = 0
        self._mouse_watcher = None
        self._picker = CollisionTraverser()  # Make a traverser
        self._pq = CollisionHandlerQueue()  # Make a handler
        self._pickerNode = CollisionNode('mouseRay')
        self._pickerNP = camera.attach_new_node(self._pickerNode)
        self._pickerRay = CollisionRay()  # Make our ray
        self._pickerNode.addSolid(self._pickerRay)
        self._picker.addCollider(self._pickerNP, self._pq)
        self._pickerNode.set_into_collide_mask(0)

        self.raycast = True
        self.collision = None
        self.collisions = []
        self.enabled = True

    @property
    def x(self):
        if not self._mouse_watcher.has_mouse():
            return 0
        return self._mouse_watcher.getMouseX() / 2 * window.aspect_ratio  # same space as ui stuff

    @x.setter
    def x(self, value):
        self.position = (value, self.y)


    @property
    def y(self):
        if not self._mouse_watcher.has_mouse():
            return 0

        return self._mouse_watcher.getMouseY() / 2

    @y.setter
    def y(self, value):
        self.position = (self.x, value)


    @property
    def position(self):
        return Vec3(self.x, self.y, 0)

    @position.setter
    def position(self, value):
        base.win.move_pointer(
            0,
            round(value[0] + (window.size[0]/2) + (value[0]/2*window.size[0]) *1.124), # no idea why I have * with 1.124
            round(value[1] + (window.size[1]/2) - (value[1]*window.size[1])),
        )

    def __setattr__(self, name, value):

        if name == 'visible':
            window.set_cursor_hidden(not value)
            if application.base:
                application.base.win.requestProperties(window)

        if name == 'locked':
            try:
                object.__setattr__(self, name, value)
                window.set_cursor_hidden(value)
                if value:
                    window.set_mouse_mode(window.M_relative)
                else:
                    window.set_mouse_mode(window.M_absolute)

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
                if hasattr(self.hovered_entity, 'on_click') and callable(self.hovered_entity.on_click):
                    try:
                        self.hovered_entity.on_click()
                    except Exception as e:
                        print(traceback.format_exc())
                        application.quit()

                for s in self.hovered_entity.scripts:
                    if hasattr(s, 'on_click') and callable(s.on_click):
                        s.on_click()

            # double click
            if time.time() - self.prev_click_time <= self.double_click_distance:
                if abs(self.x-self.prev_click_pos[0]) > self.double_click_movement_limit or abs(self.y-self.prev_click_pos[1]) > self.double_click_movement_limit:
                    return # moused moved too much since previous click, so don't register double click.

                base.input('double click')
                if self.hovered_entity:
                    if hasattr(self.hovered_entity, 'on_double_click'):
                        try:
                            self.hovered_entity.on_double_click()
                        except Exception as e:
                            print(traceback.format_exc())
                            application.quit()

                    for s in self.hovered_entity.scripts:
                        if hasattr(s, 'on_double_click'):
                            s.on_double_click()

            self.prev_click_time = time.time()
            self.prev_click_pos = (self.x, self.y)


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

        self.moving = self.x + self.y != self.prev_x + self.prev_y

        if self.moving:
            if self.locked:
                self.velocity = self.position
                self.position = (0,0)
            else:
                self.velocity = Vec3(self.x - self.prev_x, (self.y - self.prev_y) / window.aspect_ratio ,0)
        else:
            self.velocity = Vec3(0,0,0)

        if self.left or self.right or self.middle:
            self.delta = Vec3(self.x - self.start_x, self.y - self.start_y, 0)

        self.prev_x = self.x
        self.prev_y = self.y


        self._i += 1
        if self._i < self.update_step:
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
        self._pickerRay.set_from_lens(scene.camera.lens_node, self.x * 2 / window.aspect_ratio, self.y * 2)
        if self.traverse_target:
            self._picker.traverse(self.traverse_target)

        if self._pq.get_num_entries() > 0:
            self.find_collision()
        else:
            self.collision = None
            # print('mouse miss', base.render)
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
    def normal(self): # returns the normal of the polygon, in local space.
        if not self.collision is not None:
            return None
        return Vec3(*self.collision.normal)

    @property
    def world_normal(self): # returns the normal of the polygon, in world space.
        if not self.collision is not None:
            return None
        return Vec3(*self.collision.world_normal)

    @property
    def point(self): # returns the point hit, in local space
        if self.collision is not None:
            return Vec3(*self.collision.point)
        return None

    @property
    def world_point(self): # returns the point hit, in world space
        if self.collision is not None:
            return Vec3(*self.collision.world_point)
        return None

    def find_collision(self):
        self.collisions = []
        self.collision = None
        if not self.raycast or self._pq.get_num_entries() == 0:
            self.unhover_everything_not_hit()
            return False

        self._pq.sortEntries()

        for entry in self._pq.getEntries():
            for entity in scene.entities:
                if entry.getIntoNodePath().parent == entity and entity.collision:
                    if entity.collision:
                        hit = HitInfo(
                            hit = entry.collided(),
                            entity = entity,
                            distance = distance(entry.getSurfacePoint(scene), camera.getPos()),
                            point = entry.getSurfacePoint(entity),
                            world_point = entry.getSurfacePoint(scene),
                            normal = entry.getSurfaceNormal(entity),
                            world_normal = entry.getSurfaceNormal(scene),
                            )
                        self.collisions.append(hit)
                        break

        if self.collisions:
            self.collision = self.collisions[0]
            self.hovered_entity = self.collision.entity
            if not self.hovered_entity.hovered:
                self.hovered_entity.hovered = True
                if hasattr(self.hovered_entity, 'on_mouse_enter'):
                    self.hovered_entity.on_mouse_enter()
                for s in self.hovered_entity.scripts:
                    if hasattr(s, 'on_mouse_enter'):
                        s.on_mouse_enter()


        self.unhover_everything_not_hit()



    def unhover_everything_not_hit(self):
        for e in scene.entities:
            if e == self.hovered_entity:
                continue

            if hasattr(e, 'hovered') and e.hovered:
                e.hovered = False
                if hasattr(e, 'on_mouse_exit'):
                    e.on_mouse_exit()
                for s in e.scripts:
                    if hasattr(s, 'on_mouse_exit'):
                        s.on_mouse_exit()



instance = Mouse()


if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    Button(parent=scene, text='a')

    def update():
        print(mouse.position, mouse.point)

    Cursor()
    mouse.visible = False


    app.run()
