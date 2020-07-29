from ursina import *

app = Ursina()  # create the game

cubes = []

# best to paste up text BEFORE you mess with the lights
Text(origin=(4,-18), text="default lighting")
Text(origin=(.8,-4), text="replace with dimmer ambient for these three cubes")
Text(origin=(.9,11), text="also add a bit of directional for these three cubes")

cubes.append(Entity(model='cube', color=color.red, position=(-4,3,0)))
cubes.append(Entity(model='cube', color=color.green, position=(0,3,0)))
cubes.append(Entity(model='cube', color=color.blue, position=(4,3,0)))

# add a light for all subsequent entities
Light(type='ambient', color=(0.3,0.3,0.3,1))  # full spectrum

cubes.append(Entity(model='cube', color=color.red, position=(-4,0,0)))
cubes.append(Entity(model='cube', color=color.green, position=(0,0,0)))
cubes.append(Entity(model='cube', color=color.blue, position=(4,0,0)))

# add a light for all subsequent entities
Light(type='directional', color=(0.3,0.3,0.3,1), direction=(1,1,1))  # dim full spectrum

cubes.append(Entity(model='cube', color=color.red, position=(-4,-3,0)))
cubes.append(Entity(model='cube', color=color.green, position=(0,-3,0)))
cubes.append(Entity(model='cube', color=color.blue, position=(4,-3,0)))


def update():
    for i in cubes:
        i.rotation_x += .3
        i.rotation_y += .3
        i.rotation_z += .2


app.run()   # opens a window and starts the game.
