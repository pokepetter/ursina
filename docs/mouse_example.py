from ursina import *

app = Ursina()

cursor_3d = Entity(model='icosphere', scale=.1, color=color.azure)
plane = Entity(model='plane', scale=10, collider='box', color=color.light_gray)
EditorCamera(rotation_x=30)

def update():
    if mouse.world_point:
        cursor_3d.position = mouse.world_point

app.run()