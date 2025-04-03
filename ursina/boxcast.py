"""
ursina/boxcast.py

This module provides a function for performing boxcasts in the Ursina engine.
A boxcast is similar to a raycast, but with width and height, allowing for more complex collision detection.

Dependencies:
- ursina.entity.Entity
- ursina.scene.instance
- ursina.vec3.Vec3
- ursina.color
- ursina.ursinastuff.invoke
"""

from ursina.entity import Entity
from ursina.scene import instance as scene
from ursina.vec3 import Vec3
from ursina import color
from ursina.ursinastuff import invoke

# Create a global box entity for performing boxcasts
_boxcast_box = Entity(model='cube', origin_z=-.5, collider='box', color=color.white33, enabled=False, eternal=True, add_to_scene_entities=False)

def boxcast(origin, direction=(0,0,1), distance=9999, thickness=(1,1), traverse_target=scene, ignore:list=None, debug=False):
    """
    Perform a boxcast from the origin in the specified direction.

    Args:
        origin (Vec3): The starting point of the boxcast.
        direction (tuple): The direction of the boxcast. Defaults to (0,0,1).
        distance (float): The distance the boxcast should travel. Defaults to 9999.
        thickness (tuple): The width and height of the box. Defaults to (1,1).
        traverse_target (Entity): The target entity to traverse. Defaults to scene.
        ignore (list, optional): A list of entities to ignore. Defaults to None.
        debug (bool, optional): Whether to enable debug mode. Defaults to False.

    Returns:
        HitInfo: Information about the hit, if any.
    """
    if not ignore:
        ignore = []

    if isinstance(thickness, (int, float, complex)):
        thickness = (thickness, thickness)

    # Enable the box entity and set its properties
    _boxcast_box.enabled = True
    _boxcast_box.collision = True
    _boxcast_box.position = origin
    _boxcast_box.scale = Vec3(abs(thickness[0]), abs(thickness[1]), abs(distance))
    _boxcast_box.always_on_top = debug
    _boxcast_box.visible = debug

    # Rotate the box entity to face the direction of the boxcast
    _boxcast_box.look_at(origin + direction)
    hit_info = _boxcast_box.intersects(traverse_target=traverse_target, ignore=ignore)

    if debug:
        _boxcast_box.collision = False
        invoke(setattr, _boxcast_box, 'enabled', False, delay=.2)
    else:
        _boxcast_box.enabled = False

    return hit_info


if __name__ == '__main__':
    from ursina import Ursina, held_keys, camera, duplicate, raycast, time, EditorCamera
    app = Ursina()

    '''
    Casts a ray from *origin*, in *direction*, with length *distance* and returns
    a HitInfo containing information about what it hit. This ray will only hit entities with a collider.

    Use optional *traverse_target* to only be able to hit a specific entity and its children/descendants.
    Use optional *ignore* list to ignore certain entities.
    Setting debug to True will draw the line on screen.

    Example where we only move if a wall is not hit:
    '''


    class Player(Entity):
        """
        A simple player class that moves based on input and avoids walls.
        """
        def update(self):
            """
            Update the player's position based on input and avoid walls.
            """
            self.direction = Vec3(
                self.forward * (held_keys['w'] - held_keys['s'])
                + self.right * (held_keys['d'] - held_keys['a'])
                ).normalized()  # get the direction we're trying to walk in.

            origin = self.world_position + (self.up*.5) # the ray should start slightly up from the ground so we can walk up slopes or walk over small objects.
            hit_info = raycast(origin , self.direction, ignore=(self,), distance=.5, debug=False)
            if not hit_info.hit:
                self.position += self.direction * 5 * time.dt

    Player(model='cube', origin_y=-.5, color=color.orange)
    wall_left = Entity(model='cube', collider='box', scale_y=3, origin_y=-.5, color=color.azure, x=-4)
    wall_right = duplicate(wall_left, x=4)
    camera.y = 2
    app.run()

    # test
    breakpoint()
    d = Entity(parent=scene, position=(0,0,2), model='cube', color=color.orange, collider='box', scale=2)
    e = Entity(model='cube', color=color.lime)

    camera.position = (0, 15, -15)
    camera.look_at(e)
    # camera.reparent_to(e)
    speed = .01
    rotation_speed = 1
    intersection_marker = Entity(model='cube', scale=.2, color=color.red)

    def update():
        e.position += e.forward * held_keys['w'] * speed
        e.position += e.left * held_keys['a'] * speed
        e.position += e.back * held_keys['s'] * speed
        e.position += e.right * held_keys['d'] * speed

        e.rotation_y -= held_keys['q'] * rotation_speed
        e.rotation_y += held_keys['e'] * rotation_speed

        # ray = raycast(e.world_position, e.forward, 3, debug=True)
        # ray = raycast(e.world_position, e.forward, 3, debug=True)
        ray = boxcast(e.world_position, e.right, 3, debug=True)
        # print(ray.distance, ray2.distance)
        intersection_marker.world_position = ray.world_point
        intersection_marker.visible = ray.hit
        if ray.hit:
            d.color = color.azure
        else:
            d.color = color.orange

    t = time.time()
    # ray = raycast(e.world_position, e.forward, 3, debug=True)
    print(time.time() - t)
    # raycast((0,0,-2), (0,0,1), 5, debug=False)

    EditorCamera()
    app.run()
