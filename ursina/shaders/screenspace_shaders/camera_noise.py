from ursina import Shader

camera_noise_shader = Shader(
fragment='''
#version 430

uniform sampler2D tex;
uniform float noise_offset = 1;
uniform float strength = 1;
in vec2 uv;
out vec4 color;

void main() {
    vec3 rgb = texture(tex, uv).rgb;

    float noise = fract(sin(dot(uv+noise_offset, vec2(12.9898, 78.233))) * 43758.5453);
    noise -= .5;
    noise *= strength;

    rgb += noise;

    color = vec4(rgb.r, rgb.g, rgb.b, 1.0);
}

''',
geometry='',
default_input={
    'noise_offset':1,
    'strength':.2
})



if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='sphere', color=color.orange)
    e = Entity(model='cube', y=-1)
    camera.shader = camera_noise_shader
    EditorCamera()

    #camera.set_shader_input("strength", .2)
    Sky()
    def update():
        # Since there isn't really a way to generate pseudorandom numbers in GLSL by themselves, this needs to be put here, otherwise the noise will be static.
        camera.set_shader_input("noise_offset", random.randint(0, 100)/100)

    app.run()
