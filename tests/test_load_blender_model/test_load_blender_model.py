from ursina import *


app = Ursina(borderless=False)

Entity(model='blender_test_model', collider='mesh')
EditorCamera()

app.run()
