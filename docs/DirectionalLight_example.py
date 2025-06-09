from ursina import *
from ursina.shaders import lit_with_shadows_shader # you have to apply this shader to enties for them to receive shadows.

app = Ursina()
Entity.default_shader = lit_with_shadows_shader
ground = Entity(model='plane', scale=10, texture='grass')
lit_cube = Entity(model='cube', y=1, color=color.light_gray)

light = DirectionalLight()
light.look_at(Vec3(1,-1,1))

shadow_bounds_box = Entity(model='wireframe_cube', scale=5, visible=0)
light.update_bounds(shadow_bounds_box)

EditorCamera(rotation=(30,30,0))
Sky()
app.run()