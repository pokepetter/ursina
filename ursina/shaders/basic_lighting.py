from panda3d.core import Shader


empty_shader = Shader.make(Shader.SL_GLSL,
vertex='''
#version 130
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 transform_matrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
in vec3 p3d_Normal;
out vec2 texcoord;
out vec3 world_space_normal;

void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  texcoord = p3d_MultiTexCoord0;

  vec4 invcamx = transform_matrix[0];
  vec4 invcamy = transform_matrix[1];
  vec4 invcamz = transform_matrix[2];
  vec4 invcamw = transform_matrix[3];

  mat3 invcam = mat3(
                          invcamx[0], invcamx[1], invcamx[2],
                          invcamy[0], invcamy[1], invcamy[2],
                          invcamz[0], invcamz[1], invcamz[2]
                      );

  world_space_normal = normalize(p3d_Normal * invcam);
}
''',

fragment='''
#version 130

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoord;
in vec3 world_space_normal;
out vec4 fragColor;


void main() {
    vec4 norm = vec4(world_space_normal*0.5+0.5, 1);
    float grey = 0.21 * norm.r + 0.71 * norm.g + 0.07 * norm.b;
    norm = vec4(grey, grey, grey, 1);
    vec4 color = texture(p3d_Texture0, texcoord) * p3d_ColorScale * norm;
    // float m = (color.r + color.g + color.b) / 3;
    // color = vec4(grey, grey, grey, 1);
    fragColor = color.rgba;
}


''', geometry='')


if __name__ == '__main__':
    from ursina import *
    from ursina.prefabs.primitives import *
    app = Ursina()
    window.color=color.black

    # e = Entity(model='sphere', shader=empty_shader)
    # e.setShaderInput('transform_matrix', e.getNetTransform().getMat())
    shader = empty_shader

    a = WhiteCube(shader=shader)
    a.setShaderInput('transform_matrix', a.getNetTransform().getMat())

    b = AzureSphere(shader=shader, rotation_y=180, x=3)
    b.set_shader_input('transform_matrix', b.getNetTransform().getMat())
    # AzureSphere(shader=a.shader, y=2)
    GrayPlane(scale=10, y=-2, texture='shore')

    Sky(color=color.light_gray)
    EditorCamera()

    def update():
        b.rotation_y += 1
        b.set_shader_input('transform_matrix', b.getNetTransform().getMat())
    # EditorCamera()

    app.run()
