from ursina import *


app = Ursina(size=(1280,720))

camera.orthographic = True  # remove perspective
camera.fov = 720            # set the height of the camera to be 720 units

Sprite.ppu = 1  # pixels per unit
player = Sprite('ursina_wink_0000')

def update():
    player.x += int(held_keys['d'] * 1)     # move 10 pixels per second


app.run()
