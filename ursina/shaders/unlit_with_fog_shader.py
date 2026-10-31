from ursina.shaders.unlit_shader import unlit_shader
from ursina.shaders.fog_shader import fog_shader

unlit_with_fog_shader = unlit_shader + fog_shader
unlit_with_fog_shader.name = 'unlit_with_fog_shader'
unlit_shader.compile()

if __name__ == '__main__':
    from ursina import EditorCamera, Entity, Ursina, color, Vec2, scene
    app = Ursina()

    shader = unlit_with_fog_shader

    a = Entity(model='cube', shader=shader)
    ground = Entity(model='plane', color=color.gray, scale=10, y=-2, texture='shore', shader=shader, texture_scale=(10,10))
    ground.set_shader_input('texture_scale', Vec2(2, 1))
    #Sky(color=color.light_gray)
    EditorCamera()

    scene.fog_color = color.blue
    scene.fog_density = (0, 100)

    # def input(key):
    #     if key == 'b':
    #         unlit_with_fog_shader.fog_color = color.blue

    app.run()
