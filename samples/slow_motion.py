from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController


app = Ursina()

ground = Entity(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture='white_cube', texture_scale=(100,100), collider='box')

e = Entity(model='cube', scale=(1,5,10), x=2, y=.01, rotation_y=45, collider='box', texture='white_cube')
e.texture_scale = (e.scale_z, e.scale_y)

e = Entity(model='cube', scale=(1,5,10), x=-2, y=.01, collider='box', texture='white_cube')
e.texture_scale = (e.scale_z, e.scale_y)

player = FirstPersonController(model='cube', y=1, origin_y=-.5)
player.gun = None

gun = Button(parent=scene, model='cube', color=color.blue, origin_y=-.5, position=(3,0,3), collider='box')
gun.on_click = Sequence(Func(setattr, gun, 'parent', camera), Func(setattr, player, 'gun', gun))

gun_2 = duplicate(gun, z=7, x=8)
slope = Entity(model='cube', collider='box', position=(0,0,8), scale=6, rotation=(45,0,0), texture='brick', texture_scale=(8,8))
slope = Entity(model='cube', collider='box', position=(5,0,10), scale=6, rotation=(80,0,0), texture='brick', texture_scale=(8,8))
Text('press tab to toggle slow motion', y=.5)

def input(key):
    if key == 'left mouse down' and player.gun:
        gun.blink(color.orange)
        bullet = Entity(parent=gun, model='cube', scale=.1, color=color.black)
        bullet.world_parent = scene
        bullet.animate_position(bullet.position+(bullet.forward*50), curve=curve.linear, duration=1)
        destroy(bullet, delay=1)

    if key == 'tab':
        # application.paused = not application.paused
        if application.time_scale == 1:
            application.time_scale = .3
        else:
            application.time_scale = 1



app.run()
