from ursina import Shader

camera_noise_shader = Shader(
fragment='''
#version 430

uniform sampler2D tex;
uniform vec3 noise_offset = vec3(1.0, 1.0, 1.0);
uniform float strength = 1.0;
in vec2 uv;
out vec4 color;

void main() {
    vec3 rgb = texture(tex, uv).rgb;

    // Compute per-channel noise using vec3 offset
    vec3 noise = vec3(
        fract(sin(dot(uv + noise_offset.rg, vec2(12.9898, 78.233))) * 43758.5453),
        fract(sin(dot(uv + noise_offset.gb, vec2(12.9898, 78.233))) * 43758.5453),
        fract(sin(dot(uv + noise_offset.br, vec2(12.9898, 78.233))) * 43758.5453)
    );

    noise -= 0.5;     // center around 0
    noise *= strength; // scale noise

    rgb += noise; // add noise per channel

    color = vec4(rgb, 1.0);
}

''',
geometry='',
default_input={
    'noise_offset':2,
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
        camera.set_shader_input("noise_offset", Vec3(*(random.randint(0, 100)/100 for _ in range(3))))

    app.run()
