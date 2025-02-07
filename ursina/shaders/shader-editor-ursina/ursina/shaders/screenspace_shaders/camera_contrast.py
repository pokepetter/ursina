from ursina import Shader; camera_contrast_shader = Shader(fragment='''
#version 430

uniform sampler2D tex;
uniform float contrast = 1.;

in vec2 uv;
out vec4 out_color;



void main() {
    vec4 color = texture(tex, uv).rgba;
    color.rgb = clamp(mix(vec3(0.5, 0.5, 0.5), color.rgb, contrast), 0., 1.);   // adjust contrast
    out_color = color;
}


''',
default_input={
    'contrast': 1,
}
)




if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='sphere')
    e = Entity(model='cube', y=-1)
    camera.shader = camera_contrast_shader
    camera.set_shader_input('contrast', 1)

    slider = ThinSlider(max=2, dynamic=True, position=(-.25, -.45))
    def adjust_contrast():
        camera.set_shader_input("contrast", slider.value)
    slider.on_value_changed = adjust_contrast

    EditorCamera()

    app.run()
