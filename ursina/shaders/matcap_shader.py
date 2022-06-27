from ursina import *; matcap_shader = Shader(name='matcap_shader', language=Shader.GLSL, vertex = '''#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;

out vec3 eye;
out vec3 view_normal;
// reflect alternative:
// r = e - 2. * dot( n, e ) * n;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

    eye = normalize(vec3(p3d_ModelViewMatrix * vec4(p3d_Vertex.xyz, 1.0)));
    view_normal = normalize( p3d_NormalMatrix * p3d_Normal );
}
''',
fragment='''
#version 130
uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;

in vec3 eye;
in vec3 view_normal;
out vec4 fragColor;

void main() {

    vec3 r = reflect( eye, view_normal );
    float m = 2. * sqrt( pow( r.x, 2. ) + pow( r.y, 2. ) + pow( r.z + 1., 2. ) );
    vec2 vN = r.xy / m + .5;

    vec3 base = texture2D( p3d_Texture0, vN ).rgb;
    // vec3 base = texture2D( p3d_Texture0, uv ).rgb;
    fragColor = vec4( base, 1. ) * p3d_ColorScale;
}

''',
)



if __name__ == '__main__':
    from ursina import *
    from ursina.prefabs.primitives import *
    app = Ursina()
    window.color=color.black

    shader = matcap_shader

    a = WhiteCube(shader=shader, texture='shore')
    b = WhiteSphere(shader=shader, rotation_y=180, x=3, texture='shore')
    # AzureSphere(shader=a.shader, y=2)
    GrayPlane(scale=10, y=-2, texture='shore')

    Sky(color=color.light_gray)
    EditorCamera()

    def update():
        b.rotation_z += 1
        b.rotation_y += 1
        b.rotation_x += 1
    # EditorCamera()
    print('-----------------', repr(a.shader))
    app.run()
