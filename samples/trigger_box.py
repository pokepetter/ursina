from ursina import *


app = Ursina()

player = Entity(model='cube', color=color.orange, collider='box', origin_y=-.5)
trigger_box = Entity(model='wireframe_cube', color=color.gray, scale=2, collider='box', position=Vec3(1,0,2), origin_y=-.5)
EditorCamera()

def update():
    player.z += (held_keys['w'] - held_keys['s']) * time.dt * 6
    player.x += (held_keys['d'] - held_keys['a']) * time.dt * 6

    if player.intersects(trigger_box):
        trigger_box.color = color.lime
        print('player is inside trigger box')
    else:
        trigger_box.color = color.gray

app.run()
