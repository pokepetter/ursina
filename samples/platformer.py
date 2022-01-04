import time
# t = time.time()

from ursina import *
from ursina.prefabs.platformer_controller_2d import PlatformerController2d

# window.vsync = False
window.borderless = False
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

random.seed(4)
for _ in range(10):
    Entity(
        model='cube', color=color.dark_gray, collider='box', ignore=True,
        position=(random.randint(-20,20), random.randint(0,10)),
        scale=(random.randint(1,20), random.randint(2,5), 10)
        )
# ground = Entity(model='cube', color=color.white33, origin_y=.5, scale=(20, 10, 1), collider='box')
# wall = Entity(model='cube', color=color.azure, origin=(-.5,.5), scale=(5,10), x=10, y=.5, collider='box')
# ceiling = Entity(model='cube', color=color.white33, origin_y=.5, scale=(10, 1, 1), y=4, collider='box')

player = PlatformerController2d()
player.x=1
player.y = raycast(player.world_position, player.down).world_point[1] + .01
camera.add_script(SmoothFollow(target=player, offset=[0,5,-30], speed=4))


# def update():
#     print(player.grounded)

# window.size = (window.fullscreen_size[0]//2, window.fullscreen_size[1]//2)
# window.position = (int(window.size[0]), int(window.size[1]-(window.size[1]/2)))
# window.borderless = False
# window.fullscreen = False

input_handler.bind('right arrow', 'd')
input_handler.bind('left arrow', 'a')
input_handler.bind('up arrow', 'space')
input_handler.bind('gamepad dpad right', 'd')
input_handler.bind('gamepad dpad left', 'a')
input_handler.bind('gamepad a', 'space')
# print('---------', time.time() - t)
# print(Path(sys.executable).parent)

# test
player.add_script(NoclipMode2d())

app.run()
