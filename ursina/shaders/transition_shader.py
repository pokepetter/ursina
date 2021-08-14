from ursina import *;
transition_shader = Shader(language=Shader.GLSL, fragment='''
#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;

in vec2 uv;
out vec4 fragColor;

uniform sampler2D mask_texture;
uniform float cutoff;
uniform float smooth_size;

void main() {
    vec3 color = texture2D(p3d_Texture0, uv).rgb * p3d_ColorScale.rgb;
    float value = texture(mask_texture, uv).a;
    float alpha = smoothstep(cutoff, cutoff + smooth_size, value * (1.0 - smooth_size) + smooth_size);

    fragColor = vec4(color.rgb, alpha * p3d_ColorScale.a);
}

''',

default_input = {
    'cutoff' : 0,
    'smooth_size' : 0,
}
)

if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    window.color = color._16

    e = Entity(model='quad', shader=transition_shader, texture='shore')
    mask = load_texture('radial_gradient')
    e.set_shader_input('mask_texture', mask)
    EditorCamera()

    cutoff_slider = Slider(0, 1, dynamic=True)
    def on_value_changed():
        e.set_shader_input('cutoff', cutoff_slider.value)
    cutoff_slider.on_value_changed = on_value_changed

    smooth_slider = Slider(0, 1, y=-.1, dynamic=True)
    def on_value_changed():
        e.set_shader_input('smooth_size', smooth_slider.value)
    smooth_slider.on_value_changed = on_value_changed



    # Sprite('radial_gradient')

    app.run()
