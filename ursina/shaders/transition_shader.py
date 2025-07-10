from ursina import color
from ursina.shader import Shader

transition_shader = Shader(name='transition_shader', language=Shader.GLSL, fragment='''
#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;

in vec2 uv;
out vec4 COLOR;

uniform sampler2D mask_texture;
uniform float min_cutoff;
uniform float max_cutoff;
uniform float smooth_size;

void main() {
    vec3 color = texture2D(p3d_Texture0, uv).rgb * p3d_ColorScale.rgb;
    float value = texture(mask_texture, uv).r;

    float alpha = 1.;
    if (value <= min_cutoff || value > max_cutoff) {
        alpha = 0.;
    }

    COLOR = vec4(color.rgb, alpha * p3d_ColorScale.a);
}

''',

default_input = {
    'min_cutoff' : 0,
    'max_cutoff' : 1,
    'smooth_size' : .25,
}
)

if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    window.color = color._16
    Texture.default_filtering = 'bilinear'

    e = Entity(model='quad', shader=transition_shader, scale=5, cutoff=0,
        texture='shore', color=color.azure
        )
    # mask = load_texture('explosion_particle')
    # mask = load_texture('transition_shader_example_texture')
    # mask = load_texture('perlin_noise')
    mask = load_texture('shore')
    # print(mask)
    e.set_shader_input('mask_texture', mask)
    EditorCamera()

    min_cutoff_slider = Slider(0, 1, dynamic=True, y=-.4)
    def on_value_changed():
        e.set_shader_input('min_cutoff', min_cutoff_slider.value)
    min_cutoff_slider.on_value_changed = on_value_changed

    max_cutoff_slider = Slider(0, 1, default=1, dynamic=True, y=-.45)
    def on_value_changed():
        e.set_shader_input('max_cutoff', max_cutoff_slider.value)
    max_cutoff_slider.on_value_changed = on_value_changed

    # smooth_slider = Slider(0, 1, dynamic=True, y=-.45)
    # def on_value_changed():
    #     e.set_shader_input('smooth_size', smooth_slider.value)
    # smooth_slider.on_value_changed = on_value_changed

    def input(key):
        if key == 'space':
            e.cutoff = 0
            e.animate('cutoff', 1, duration=.1, curve=curve.linear, delay=.05)
        # e.scale=4
        # e.animate('scale', Vec3(7,7,7), duration=.1, curve=curve.linear, delay=.05)

    # Sprite('radial_gradient')

    app.run()
