"""
ursina/mouse.py

This module defines the Mouse class, which handles mouse input and interactions in the Ursina engine.
It provides functionality for tracking mouse position, velocity, clicks, and collisions with entities.

Dependencies:
- time
- panda3d.core.CollisionTraverser
- panda3d.core.CollisionNode
- panda3d.core.CollisionHandlerQueue
- panda3d.core.CollisionRay
- ursina.application
- ursina.window
- ursina.scene
- ursina.camera
- ursina.hit_info
- ursina.vec3
- ursina.ursinamath
"""

import time
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from ursina import application
from ursina.window import instance as window
from ursina.scene import instance as scene
from ursina.camera import instance as camera
from ursina.hit_info import HitInfo
from ursina.vec3 import Vec3
from ursina.ursinamath import distance


class Mouse:
    """
    The Mouse class handles mouse input and interactions in the Ursina engine.
    It provides functionality for tracking mouse position, velocity, clicks, and collisions with entities.

    Attributes:
        enabled (bool): Whether the mouse is enabled.
        visible (bool): Whether the mouse cursor is visible.
        locked (bool): Whether the mouse cursor is locked to the center of the screen.
        position (Vec3): The current position of the mouse.
        delta (Vec3): The movement of the mouse since the last click.
        prev_x (float): The previous x-coordinate of the mouse.
        prev_y (float): The previous y-coordinate of the mouse.
        start_x (float): The x-coordinate of the mouse when a button was pressed.
        start_y (float): The y-coordinate of the mouse when a button was pressed.
        velocity (Vec3): The current velocity of the mouse.
        moving (bool): Whether the mouse is currently moving.
        prev_click_time (float): The time of the previous click.
        prev_click_pos (tuple): The position of the previous click.
        double_click_distance (float): The maximum time between clicks to register a double click.
        double_click_movement_limit (float): The maximum movement between clicks to register a double click.
        hovered_entity (Entity): The entity currently hovered by the mouse.
        left (bool): Whether the left mouse button is pressed.
        right (bool): Whether the right mouse button is pressed.
        middle (bool): Whether the middle mouse button is pressed.
        delta_drag (Vec3): The movement of the mouse between left mouse down and left mouse up.
        update_step (int): The number of frames between updates.
        traverse_target (NodePath): The target node to traverse for collisions.
        _i (int): Internal counter for update steps.
        _mouse_watcher (MouseWatcher): The Panda3D MouseWatcher object.
        _picker (CollisionTraverser): The collision traverser for mouse picking.
        _pq (CollisionHandlerQueue): The collision handler queue for mouse picking.
        _pickerNode (CollisionNode): The collision node for the mouse ray.
        _pickerNP (NodePath): The node path for the mouse ray.
        _pickerRay (CollisionRay): The collision ray for mouse picking.
        raycast (bool): Whether to perform raycasting for collisions.
        collision (HitInfo): The current collision information.
        collisions (list): A list of all collisions.
    """

    def __init__(self):
        """
        Initialize the Mouse object with default values.
        """
        self.enabled = False
        self.visible = True
        self.locked = False
        self._locked_mouse_last_frame = False
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
        """
        Get the x-coordinate of the mouse in the window.

        Returns:
            float: The x-coordinate of the mouse.
        """
        pointer = base.win.get_pointer(0)
        if not pointer.in_window:
            return 0
        return ((pointer.get_x() / window.size.x) -.5) * window.aspect_ratio  # same space as ui stuff

    @x.setter
    def x(self, value):
        """
        Set the x-coordinate of the mouse in the window.

        Args:
            value (float): The x-coordinate to set.
        """
        self.position = (value, self.y)


    @property
    def y(self):
        """
        Get the y-coordinate of the mouse in the window.

        Returns:
            float: The y-coordinate of the mouse.
        """
        pointer = base.win.get_pointer(0)
        if not pointer.in_window:
            return 0
        return -((pointer.get_y() / window.size.y) -.5) # same space as ui stuff


    @y.setter
    def y(self, value):
        """
        Set the y-coordinate of the mouse in the window.

        Args:
            value (float): The y-coordinate to set.
        """
        self.position = (self.x, value)


    @property
    def position(self):
        """
        Get the position of the mouse in the window.

        Returns:
            Vec3: The position of the mouse.
        """
        return Vec3(self.x, self.y, 0)

    @position.setter
    def position(self, value):
        """
        Set the position of the mouse in the window.

        Args:
            value (Vec3): The position to set.
        """
        if not application.base:
            return
        application.base.win.move_pointer(
            0,
            round(value[0] + (window.size[0]/2) + (value[0]/2*window.size[0]) *1.124), # no idea why I have * with 1.124
            round(value[1] + (window.size[1]/2) - (value[1]*window.size[1])),
        )

    @property
    def locked(self):
        """
        Get whether the mouse cursor is locked to the center of the screen.

        Returns:
            bool: True if the mouse cursor is locked, False otherwise.
        """
        if not hasattr(self, '_locked'):
            return False
        return self._locked

    @locked.setter
    def locked(self, value):
        """
        Set whether the mouse cursor is locked to the center of the screen.

        Args:
            value (bool): True to lock the mouse cursor, False to unlock it.
        """
        self._locked = value
        if value:
            window.set_mouse_mode(window.M_confined)
        else:
            window.set_mouse_mode(window.M_absolute)

        if not application.base:
            return

        # print('return', value)
        # self.position = Vec3(0,0,0)
        window.set_cursor_hidden(value)
        application.base.win.requestProperties(window)
        self._locked_mouse_last_frame = True


    @property
    def visible(self):
        """
        Get whether the mouse cursor is visible.

        Returns:
            bool: True if the mouse cursor is visible, False otherwise.
        """
        if not hasattr(self, '_visible'):
            return True
        return self._visible

    @visible.setter
    def visible(self, value):
        """
        Set whether the mouse cursor is visible.

        Args:
            value (bool): True to make the mouse cursor visible, False to hide it.
        """
        self._visible = value
        window.set_cursor_hidden(!value)
        if application.base:
            # window.position = window.position
            application.base.win.requestProperties(window)


    def input(self, key):
        """
        Handle input events for the mouse.

        Args:
            key (str): The input key.
        """
        if not self.enabled:
            return

        if key.endswith('mouse down'):
            self.start_x = self.x
            self.start_y = self.y

        elif key.endswith('mouse up'):
            self.delta_drag = Vec3(self.x-self.start_x, self.y-self.start_y, 0)

        if key == 'left mouse down':
            self.left = True
            if self.hovered_entity:
                if self.hovered_entity.on_click:
                    self.hovered_entity.on_click()

                for s in self.hovered_entity.scripts:
                    if hasattr(s, 'on_click') and s.on_click:
                        s.on_click()

            # double click
            if time.time() - self.prev_click_time <= self.double_click_distance:
                if self.prev_click_pos and (abs(self.x-self.prev_click_pos[0]) > self.double_click_movement_limit or abs(self.y-self.prev_click_pos[1]) > self.double_click_movement_limit):
                    return # moused moved too much since previous click, so don't register double click.

                application.base.input('double click')
                if self.hovered_entity:
                    if hasattr(self.hovered_entity, 'on_double_click') and self.hovered_entity.on_double_click:
                            self.hovered_entity.on_double_click()

                    for s in self.hovered_entity.scripts:
                        if hasattr(s, 'on_double_click') and s.on_double_click:
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
        """
        Update the mouse state, including position, velocity, and collisions.
        """
        if application.window_type != 'onscreen':
            return

        if not self.enabled or not self._mouse_watcher.has_mouse() or self._locked_mouse_last_frame:
            self.velocity = Vec3(0,0,0)
            self._locked_mouse_last_frame = False
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
    def normal(self): 
        """
        Get the normal of the polygon at the collision point in local space.

        Returns:
            Vec3: The normal vector at the collision point.
        """
        if not self.collision is not None:
            return None
        return Vec3(*self.collision.normal)

    @property
    def world_normal(self): 
        """
        Get the normal of the polygon at the collision point in world space.

        Returns:
            Vec3: The normal vector at the collision point.
        """
        if not self.collision is not None:
            return None
        return Vec3(*self.collision.world_normal)

    @property
    def point(self): 
        """
        Get the point of collision in local space.

        Returns:
            Vec3: The point of collision.
        """
        if self.collision is not None:
            return Vec3(*self.collision.point)
        return None

    @property
    def world_point(self): 
        """
        Get the point of collision in world space.

        Returns:
            Vec3: The point of collision.
        """
        if self.collision is not None:
            return Vec3(*self.collision.world_point)
        return None

    @property
    def is_outside(self):
        """
        Check if the mouse is outside the window.

        Returns:
            bool: True if the mouse is outside the window, False otherwise.
        """
        return not self._mouse_watcher.has_mouse()


    def find_collision(self):
        """
        Find the collision information for the mouse ray.

        Returns:
            bool: True if a collision was found, False otherwise.
        """
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
        """
        Unhover all entities that are not currently hit by the mouse ray.
        """
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
    from ursina import Ursina, Button, mouse
    app = Ursina()
    Button(parent=scene, text='a')

    def input(key):
        if key == 'space':
            mouse.locked = not mouse.locked
            print(mouse.velocity)

    Cursor()
    # mouse.visible = False


    app.run()
