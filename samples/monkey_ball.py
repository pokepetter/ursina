from ursina import *

app = Ursina()

rotation_resetter = Entity()
cube = Entity(parent=rotation_resetter, model='cube', texture='white_cube')


def update():
    rotation_resetter.rotation_x += 100 * (held_keys['a'] - held_keys['d']) * time.dt
    rotation_resetter.rotation_z += 100 * (held_keys['w'] - held_keys['s']) * time.dt

    cube.rotation = cube.world_rotation
    rotation_resetter.rotation = (0,0,0)

EditorCamera()

app.run()
