from ursina import *                    # this will import everything we need from ursina with just one line.

class Player(Entity):                   # inherits Entity, ursina's 'god class'
    def __init__(self):
        super().__init__()
        self.model = 'cube'             # finds a 3d model by name
        self.color = color.orange
        self.scale_y = 2

    def update(self):               # because Player is an Entity, update gets automatically called by the engine.
        self.x += held_keys['d'] * 1/128
        self.x -= held_keys['a'] * 1/128


app = Ursina()
s = Sprite(texture='beach_level_pattern')
camera.orthographic = True
camera.fov = 1

player = Player()
player.scale *= 1/128 * 16
camera.world_parent = player
app.run()                               # opens a window and starts the game.
