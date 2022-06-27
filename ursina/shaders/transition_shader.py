from ursina import *;
transition_shader = Shader(name='transition_shader', language=Shader.GLSL, fragment='''
#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;

in vec2 uv;
out vec4 COLOR;

uniform sampler2D mask_texture;
uniform float cutoff;
uniform float smooth_size;

void main() {
    vec3 color = texture2D(p3d_Texture0, uv).rgb * p3d_ColorScale.rgb;
    float value = texture(mask_texture, uv).r;
    float alpha = smoothstep(cutoff, cutoff + smooth_size, value * max(0.0, (1.0 - smooth_size) + smooth_size));

    COLOR = vec4(color.rgb, alpha * p3d_ColorScale.a);
}

''',

default_input = {
    'cutoff' : 0,
    'smooth_size' : .25,
}
)

if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    window.color = color._16

    e = Entity(model='quad', shader=transition_shader, scale=5, cutoff=0)
    # mask = load_texture('explosion_particle')
    mask = load_texture('explosion_particle_2')
    mask = load_texture('impactstrikey_02_b')
    print(mask)
    e.set_shader_input('mask_texture', mask)
    EditorCamera()

    cutoff_slider = Slider(0, 1, dynamic=True, y=-.4)
    def on_value_changed():
        e.set_shader_input('cutoff', cutoff_slider.value)
    cutoff_slider.on_value_changed = on_value_changed

    smooth_slider = Slider(0, 1, dynamic=True, y=-.45)
    def on_value_changed():
        e.set_shader_input('smooth_size', smooth_slider.value)
    smooth_slider.on_value_changed = on_value_changed

    def input(key):
        if key == 'space':
            e.cutoff = 0
            e.animate('cutoff', 1, duration=.1, curve=curve.linear, delay=.05)
        # e.scale=4
        # e.animate('scale', Vec3(7,7,7), duration=.1, curve=curve.linear, delay=.05)

    # Sprite('radial_gradient')

    app.run()
