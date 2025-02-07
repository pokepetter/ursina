from ursina import *

point_shader = Shader(language=Shader.GLSL,
vertex = '''
#version 150
// uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 texcoords;
in vec4 p3d_Color;
out vec4 vertex_color;

void main() {
    gl_Position = p3d_Vertex;
    texcoords = p3d_MultiTexCoord0;
    vertex_color = p3d_Color;
}
''',
geometry='''
#version 150
layout (points) in;
layout (triangle_strip, max_vertices=3) out;

uniform mat4 p3d_ModelViewProjectionMatrix;

in vec4 vertex_color[];
out vec4 vcol;

const float size = .5;

void create_offset_vertex(vec3 offset) {
    vec4 actual_offset = vec4(offset * size, 0.0);
    vec4 world_position = gl_in[0].gl_Position + actual_offset;
    gl_Position = p3d_ModelViewProjectionMatrix * world_position;
    vcol = vertex_color[0];
    EmitVertex();
}
void main() {
    create_offset_vertex(vec3(-.1, .2, .2));
    create_offset_vertex(vec3(.1, 0, .2));
    create_offset_vertex(vec3(.1, -.2, -1));
    EndPrimitive();
}

''',

fragment='''
#version 150
uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoords;
in vec4 vcol;
out vec4 fragColor;


void main() {
    vec4 color = texture(p3d_Texture0, texcoords) * p3d_ColorScale * vcol;
    fragColor = color.rgba;
}
''',
)



if __name__ == '__main__':
    from ursina import *
    from ursina.prefabs.primitives import *
    app = Ursina(vsync = False)
    window.color=color.black

    b = AzureSphere(rotation_y=180, x=3, scale=2,
        #texture='shore'
    )
    b.model.mode = 'point'
    b.model.colors = [color.random_color() for e in b.model.vertices]
    b.model.generate()
    b.shader = point_shader
    GrayPlane(scale=10, y=-2, texture='shore')

    Sky(color=color.light_gray)
    EditorCamera()

    app.run()
