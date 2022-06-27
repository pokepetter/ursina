from ursina import *


basic_lighting_shader = Shader(name='basic_lighting_shader', language=Shader.GLSL,
vertex = '''
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 texcoord;

in vec3 p3d_Normal;
out vec3 world_normal;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = p3d_MultiTexCoord0;
    world_normal = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);
}
''',

fragment='''
#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoord;
in vec3 world_normal;
out vec4 fragColor;


void main() {
    vec4 norm = vec4(world_normal*0.5+0.5, 1);
    float grey = 0.21 * norm.r + 0.71 * norm.g + 0.07 * norm.b;
    norm = vec4(grey, grey, grey, 1);
    vec4 color = texture(p3d_Texture0, texcoord) * p3d_ColorScale * norm;
    fragColor = color.rgba;
}


''', geometry='',
)


if __name__ == '__main__':
    from ursina import *
    from ursina.prefabs.primitives import *
    app = Ursina()
    window.color=color.black

    # e = Entity(model='sphere', shader=basic_lighting_shader)
    # e.setShaderInput('transform_matrix', e.getNetTransform().getMat())
    shader = basic_lighting_shader

    a = WhiteCube(shader=basic_lighting_shader)
    # a.setShaderInput('transform_matrix', a.getNetTransform().getMat())

    b = WhiteSphere(shader=basic_lighting_shader, x=3)
    # b.set_shader_input('transform_matrix', b.getNetTransform().getMat())
    # AzureSphere(shader=a.shader, y=2)
    GrayPlane(scale=10, y=-2, texture='shore', shader=basic_lighting_shader)

    Sky(color=color.light_gray)
    EditorCamera()

    def update():
        b.rotation_y += 1
        #b.rotation_z += 1
        b.rotation_x += 1
        b.set_shader_input('transform_matrix', b.getNetTransform().getMat())
    # EditorCamera()

    app.run()
