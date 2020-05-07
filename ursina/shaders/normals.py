from ursina import *

normals_shader = Shader(language=Shader.GLSL,
vertex = '''
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 transform_matrix;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
out vec3 world_space_normal;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    world_space_normal = normalize(transpose( inverse(mat3(transform_matrix)) ) * p3d_Normal.xyz);
}
''',

fragment='''
#version 130

uniform vec4 p3d_ColorScale;
in vec2 texcoord;
out vec4 fragColor;
in vec3 world_space_normal;


void main() {
    fragColor = vec4(world_space_normal*0.5+0.5, 1);
    // o_color = float4(l_norm0*0.5+0.5, 1);
    // c.rgb = i.worldNormal*0.5+0.5;
}

''',
geometry='',
default_input={
    'transform_matrix': Mat4    (),
}
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
    b = AzureSphere(shader=shader, rotation_y=180, x=3)
    # AzureSphere(shader=a.shader, y=2)
    GrayPlane(scale=10, y=-2, texture='shore')

    Sky(color=color.light_gray)
    EditorCamera()

    def update():
        b.rotation_z += 1
        b.rotation_y += 1
        b.rotation_x += 1
        b.set_shader_input('transform_matrix', b.getNetTransform().getMat())
        # a.rotation_x += 1
        a.set_shader_input('transform_matrix', a.getNetTransform().getMat())
    # EditorCamera()

    app.run()
