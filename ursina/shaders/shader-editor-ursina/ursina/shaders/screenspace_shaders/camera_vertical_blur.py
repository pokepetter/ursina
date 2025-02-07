from ursina import Shader


camera_vertical_blur_shader = Shader(
fragment='''
#version 430

uniform sampler2D tex;
in vec2 uv;
uniform float blur_size;
out vec4 color;

void main() {
    color = texture(tex, uv).rgba;
    vec4 col = vec4(0.);

    for(float index=0; index<10; index++) {
        // add color at position to color
        vec2 offset_uv = uv + vec2(0, (index/9 - 0.5) * blur_size);
        col += texture(tex, offset_uv);
    }

    col = col / 10;
    col = 1-((1-color)*(1-col));
    color = mix(color, vec4(col.rgb, 1), blur_size*10);
}
''',
default_input=dict(
    blur_size = .1
))

if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    window.color = color._16

    e = Entity(model='sphere', color=color.orange)
    e = Entity(model='cube', y=-1)
    camera.shader = camera_vertical_blur_shader


    slider = ThinSlider(max=.1, dynamic=True, position=(-.25, -.45))

    def set_blur():
        print(slider.value)
        camera.set_shader_input("blur_size", slider.value)

    def update():
        camera.set_shader_input('blur_size', mouse.x)


    slider.on_value_changed = set_blur
    EditorCamera()

    app.run()
