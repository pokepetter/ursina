from ursina import *; noise_fog_shader = Shader(name='noise_fog_shader', language=Shader.GLSL, fragment='''
#version 130

uniform vec4 p3d_ColorScale;
in vec2 uv;
out vec4 result;

uniform sampler2D p3d_Texture0;
uniform float time;

uniform vec4 dark_color;
uniform vec4 light_color;

void main() {
    vec4 a = texture(p3d_Texture0, uv + vec2(time*.1, time*.1));
    vec4 b = texture(p3d_Texture0, uv - vec2(time*.1, time*.075));
    vec4 c = (a + b) * .5;

    result = texture(p3d_Texture0, uv + c.xy) * c;
    result.a = 1.0;

    result = mix(dark_color, light_color, result.r);
}

''',
default_input = {
  'dark_color' : color.black,
  'light_color' : color.white,
}
)



if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    window.color=color.black

    e = Entity(model='quad', texture='perlin_noise', shader=noise_fog_shader, scale=6)
    e.set_shader_input('dark_color', hsv(280,1,.1,0))
    e.set_shader_input('light_color', color.cyan)

    app.t = 0
    def update():
        app.t += time.dt
        e.set_shader_input('time', app.t)

    bg = Sprite('shore', scale=1, z=1, color=color.dark_gray)
    window.size *= .5
    app.run()
