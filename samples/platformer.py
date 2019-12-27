from ursina import *
from ursina.prefabs.platformer_controller_2d import PlatformerController2d


window.set_z_order(window.Z_top)

app = Ursina()
window.color = color.light_gray
camera.orthographic = True
camera.fov = 20

ground = Entity(
    model = 'cube',
    color = color.olive.tint(-.4),
    z = -.1,
    y = -1,
    origin_y = .5,
    scale = (1000, 100, 10),
    collider = 'box',
    ignore = True,
    )


random.seed(1)
for i in range(10):
    Entity(
        model='cube', color=color.dark_gray, collider='box', ignore=True,
        position=(random.randint(-20,20), random.randint(0,10)),
        scale=(random.randint(1,20), random.randint(1,5), 10)
        )


player = PlatformerController2d(color=color.green.tint(-.3))
player.y = raycast(player.world_position, player.down).world_point[1]
camera.smooth_follow.offset[1] = 5

window.size = (window.fullscreen_size[0]//2, window.fullscreen_size[1]//2)
window.position = (int(window.size[0]), int(window.size[1]-(window.size[1]/2)))
window.borderless = False
window.fullscreen = False


app.run()
