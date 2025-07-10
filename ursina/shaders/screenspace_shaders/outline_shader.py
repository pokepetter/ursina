from ursina import Func, Shader, camera, color, window

outline_shader = Shader(fragment='''
#version 430

uniform sampler2D tex;
uniform sampler2D dtex;
uniform vec2 window_size;
uniform float far = 100.;
uniform float near = 1.;
uniform vec4 outline_color;

in vec2 uv;
out vec4 out_color;

float eye_depth(float depth) {
    return far * near / ((near - far) * depth + far);
}

void main() {
    vec4 color = texture(tex, uv).rgba;
    float depth = eye_depth(texture(dtex, uv).r);

    vec2 pixel_size = vec2(1./window_size.x, 1./window_size.y);
    // vec2 pixel_size = vec2(.001);

    float n = eye_depth(texture(dtex, uv + pixel_size * vec2(0, 1)).r);
    float e = eye_depth(texture(dtex, uv + pixel_size * vec2(1, 0)).r);
    float s = eye_depth(texture(dtex, uv + pixel_size * vec2(0, -1)).r);
    float w = eye_depth(texture(dtex, uv + pixel_size * vec2(-1, 0)).r);

    if (n - s > 0.05 || w - e > 0.05 || e - w > 0.05 || s - n > 0.05)
        color = outline_color;

    out_color = color;
}
''',
default_input={
    'window_size': window.size,
    'far': Func(getattr, camera, 'clip_plane_far'),
    'near': .1,

    'outline_color': color.black,

}
)



if __name__ == '__main__':
    from ursina import *

    app = Ursina()
    e = Entity(model='sphere', color=color.white)
    e = Entity(model='cube', y=-1)
    Entity(model='plane', scale=100, y=-10)
    camera.shader = outline_shader
    camera.far_clip_plane = 1000
    camera.set_shader_input('near', .01)

    def input(key):
        if key == 'space':
            if not camera.shader:
                camera.shader = outline_shader
            else:
                camera.shader = None

    EditorCamera()

    app.run()
