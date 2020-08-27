from ursina import *
from math import floor


app = Ursina()

size = 32
plane = Entity(model='quad', color=color.azure, origin=(-.5,-.5), z=10, collider='box', scale=size) # create an invisible plane for the mouse to collide with
grid = [[Entity(model='quad', position=(x,y), texture='white_cube', enabled=False) for y in range(size)] for x in range(size)] # make 2d array of entities
player = Entity(model='quad', color=color.orange, position=(16,16,-.1))
cursor = Entity(model=Quad(mode='line'), color=color.lime)

def update():
    if mouse.hovered_entity == plane:
        # round the cursor position
        cursor.position = mouse.world_point
        cursor.x = round(cursor.x, 0)
        cursor.y = round(cursor.y, 0)

    # check the grid if the player can move there
    if held_keys['a'] and not grid[int(player.x)][int(player.y)].enabled:
        player.x -= 5 * time.dt
    if held_keys['d'] and not grid[int(player.x)+1][int(player.y)].enabled:
        player.x += 5 * time.dt



def input(key):
    if key == 'left mouse down':
        grid[int(cursor.x)][int(cursor.y)].enabled = True
    if key == 'right mouse down':
        grid[int(cursor.x)][int(cursor.y)].enabled = False


camera.orthographic = True
camera.fov = 10
camera.position = (16,18)

# enable all tiles lower than 16 to make a ground
for column in grid:
    for e in column:
        if e.y <= 15:
            e.enabled = True

app.run()
