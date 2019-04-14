from ursina import *
from ursina.prefabs.player_controller import PlayerController

class Player(PlayerController):
    def __init__(self):
        super().__init__()
        self.y = raycast(self.world_position, self.down).point[1]


app = Ursina()
# compress_textures()
window.color = color.smoke
# camera.rotation_x = -5
# camera.z = -40
camera.fov = 20
camera.orthographic = True
bg = Entity(
    model = 'quad',
    texture = 'bg',
    z = 10,
    scale = (20, 10, 1) * 5
    )

ground = Entity(
    model = 'cube',
    color = color.gray,
    z = -.1,
    y = -1,
    scale = (10, 1, 10),
    collider = 'box',
    collision = True
    )

limit_bottom = Entity(
    model = 'cube',
    color = color.magenta,
    z = -.1,
    y = -3,
    origin = (0, .5),
    scale = (50, 1, 10),
    collider = 'box',
    collision = True
    )

player = Player()
app.run()
