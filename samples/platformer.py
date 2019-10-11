from ursina import *
from ursina.prefabs.platformer_controller_2d import PlatformerController2d


app = Ursina()
window.color = color.light_gray
camera.orthographic = True
camera.fov = 20

ground = Entity(
    model = 'cube',
    color = color.dark_gray,
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


player = PlatformerController2d()
player.y = raycast(player.world_position, player.down).world_point[1]
camera.smooth_follow.offset[1] = 5


# def input(key):
#     if key == 't':
#         if application.time_scale == 1:
#             application.time_scale = .5
#         else:
#             application.time_scale = 1

app.run()
