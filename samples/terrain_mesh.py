from ursina import *


app = Ursina()

e = Entity(model=Terrain('loddefjord_height_map', skip=8), texture='loddefjord_color', scale=100, scale_y=50)
Sky(rotation_y=125)
e.model.save('loddefjord_terrain')
scene.fog_color = color.gray
scene.fog_density = .01

from ursina.prefabs.first_person_controller import FirstPersonController
# fpc = FirstPersonController(speed=10)
EditorCamera()
window.exit_button.visible = False
window.fps_counter.enabled = False
mouse.visible = False



# from ursina .shaders import camera_vertical_blur_shader
# camera.shader = camera_vertical_blur_shader
# camera.set_shader_input('blur_size', .0)
#
# camera.blur_amount = 0
# def update():
#     camera.set_shader_input("blur_size", camera.blur_amount)
#
# t = Text('It was like a dream', enabled=False, scale=3, origin=(0,0), color=color.dark_text)
#
# def input(key):
#     if key == 'space':
#         camera.animate('blur_amount', .6, duration=5)
#         invoke(t.appear, speed=.1, delay=5.2)

# window.size /= 2


app.run()
