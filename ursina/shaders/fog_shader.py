from ursina.shader import Shader
from ursina.ursinastuff import Func
from ursina.scene import instance as scene
from ursina import color
from ursina.vec2 import Vec2

'''Note: This is only a shader pass, not a stand-alone shader'''

fog_shader = Shader(name='fog_shader', language=Shader.GLSL, vertex='''\
#version 140
uniform vec4 fog_color;
uniform float fog_start;
uniform float fog_end;
out vec3 camera_world_pos;
void main() {
    // Transform vertex to camera/view space
    vec4 view_pos = p3d_ModelViewMatrix * p3d_Vertex;
    camera_world_pos = view_pos.xyz;
}
''',
fragment='''\
#version 140
in vec3 camera_world_pos;
uniform vec4 fog_color;
uniform float fog_start;
uniform float fog_end;

void main() {
    float distance_to_camera = length(camera_world_pos);  // In view space, camera is at (0,0,0), so distance is just the length of camera_world_pos
    float fog_t = smoothstep(fog_start, fog_end, distance_to_camera);
    frag_color.rgb = mix(frag_color.rgb, fog_color.rgb, fog_t * fog_color.a);
}
''',
default_input = {
    'fog_color' : Func(getattr, scene, 'fog_color'),
    'fog_start': 10,
    'fog_end': 400,
})


if __name__ == '__main__':
    from ursina import EditorCamera, Entity, Ursina
    app = Ursina()

    from ursina.shaders import unlit_shader
    shader = unlit_shader + fog_shader

    scene.fog_color = color.red
    scene.fog_density = (0, 100)

    a = Entity(model='cube', shader=shader)
    ground = Entity(model='plane', color=color.gray, scale=10, y=-2, texture='shore', shader=shader, texture_scale=(10,10))
    ground.set_shader_input('texture_scale', Vec2(2, 1))
    EditorCamera()

    # scene.fog_color = color.blue

    def input(key):
        if key == 'b':
            shader.fog_color = color.blue

    app.run()
