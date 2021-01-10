from ursina import Shader


camera_contrast_shader = Shader(
vertex='''
#version 430

in vec4 p3d_Vertex;
uniform mat4 p3d_ViewMatrixInverse;
in vec2 p3d_MultiTexCoord0;
out vec2 uv;

void main() {
    gl_Position = p3d_ViewMatrixInverse  * p3d_Vertex;
    uv = p3d_MultiTexCoord0;
}
''',

fragment='''
#version 430

uniform sampler2D tex;
in vec2 uv;
out vec4 color;

void main() {
    vec3 rgb = texture(tex, uv).rgb;
    color = vec4(rgb, 1.0);
}

''')



if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='sphere', color=color.yellow)
    e = Entity(model='cube', y=-1)
    camera.shader = camera_contrast_shader
    camera.set_shader_input('contrast', 1)

    #slider = ThinSlider(max=1, dynamic=True, position=(-.25, -.45))
    #def set_blur():
    #    camera.set_shader_input("contrast", slider.value)
    #slider.on_value_changed = set_blur

    EditorCamera()

    app.run()
