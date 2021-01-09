from ursina import *

normals_shader = Shader(language=Shader.GLSL,
vertex = '''
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
out vec3 world_normal;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    world_normal = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);
}
''',

fragment='''
#version 130

uniform vec4 p3d_ColorScale;
in vec2 texcoord;
out vec4 fragColor;
in vec3 world_normal;


void main() {
    fragColor = vec4(world_normal*0.5+0.5, 1);
}

''',
geometry='',
)



if __name__ == '__main__':
    from ursina import *
    from ursina.prefabs.primitives import *
    app = Ursina()
    window.color=color.black

    # e = Entity(model='sphere', shader=normals_shader)
    # e.setShaderInput('transform_matrix', e.getNetTransform().getMat())
    shader = normals_shader

    a = WhiteCube(shader=shader)
    b = AzureSphere(rotation_y=180, x=3)
    b.shader = shader
    # AzureSphere(shader=a.shader, y=2)
    GrayPlane(scale=10, y=-2, texture='shore')

    Sky(color=color.light_gray)
    EditorCamera()

    def update():
        b.rotation_z += 1
        b.rotation_y += 1
        b.rotation_x += 1
        # a.rotation_x += 1
    # EditorCamera()

    app.run()
