from ursina import camera, color, window
from ursina.shader import Shader
from ursina.ursinastuff import Func
from ursina.vec2 import Vec2
from ursina.vec3 import Vec3

unlit_points_shader = Shader(name='unlit_points_shader', language=Shader.GLSL,
vertex='''
#version 330 core

layout(location = 0) in vec4 p3d_Vertex;
layout(location = 1) in vec4 color;  // Vertex color input
layout(location = 2) in vec2 p3d_MultiTexCoord0;

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p3d_ModelMatrix; // Model matrix for converting to world space

out vec4 vertex_color;
out vec2 texCoord;
out vec3 vertex_world_position;
out float point_size; // Output point size based on distance from the camera

void main() {
    // Calculate the world position of the vertex
    vertex_world_position = (p3d_ModelMatrix * p3d_Vertex).xyz;

    // Calculate the camera position by inverting the ModelView matrix and applying it to the origin
    vec4 camera_position = inverse(p3d_ModelViewMatrix) * vec4(0.0, 0.0, 0.0, 1.0);

    // Calculate the distance from the camera to the vertex
    float distance = length(camera_position.xyz - vertex_world_position);

    // Set the point size based on the distance (you can adjust this formula as needed)
    point_size = 1.0 / distance; // Example: Inverse distance scaling (adjust as needed)

    // Apply the model view matrix to position the vertex
    gl_Position = p3d_ModelViewMatrix * p3d_Vertex;

    // Pass color and texture coordinates to the next shader stage
    vertex_color = color;
    texCoord = p3d_MultiTexCoord0;
}

''',

geometry='''
#version 330 core
layout(points) in;
layout(triangle_strip, max_vertices = 4) out;

uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p3d_ViewMatrix;
uniform float point_size;
uniform bool perspective_scaling;
uniform vec2 window_size;

out vec2 texCoord;
in vec4 vertex_color[];
out vec4 vert_col;
in vec3 vertex_world_position;



void main() {
    vec4 view_pos = gl_in[0].gl_Position;
    vec4 clip_pos = p3d_ProjectionMatrix * view_pos;


    float ndc_size = point_size / max(window_size.x, window_size.y) * 2.0;
    if (perspective_scaling) {
    }

    vec3 camera_right = vec3(1.,0,0);
    vec3 camera_up = vec3(0,1,0);
    vec3 right_offset = camera_right * (ndc_size * 0.5 * clip_pos.w);
    vec3 up_offset = camera_up * (ndc_size * 0.5 * clip_pos.w);

    vert_col = vertex_color[0];
    // Emit four vertices to form a quad facing the camera
    texCoord = vec2(0, 0);
    gl_Position = p3d_ProjectionMatrix * (view_pos - vec4(right_offset + up_offset, 0.0));
    EmitVertex();

    texCoord = vec2(1, 0);
    gl_Position = p3d_ProjectionMatrix * (view_pos + vec4(right_offset - up_offset, 0.0));
    EmitVertex();

    texCoord = vec2(0, 1);
    gl_Position = p3d_ProjectionMatrix * (view_pos - vec4(right_offset - up_offset, 0.0));
    EmitVertex();

    texCoord = vec2(1, 1);
    gl_Position = p3d_ProjectionMatrix * (view_pos + vec4(right_offset + up_offset, 0.0));
    EmitVertex();

    EndPrimitive();
}
''',


fragment='''
#version 330 core

in vec4 vert_col;
in vec2 texCoord;
uniform sampler2D p3d_Texture0;
out vec4 fragColor;

void main() {
    vec4 texColor = texture(p3d_Texture0, texCoord);
    fragColor = texColor * vert_col;
}

''',
default_input={
    'texture_scale' : Vec2(1,1),
    'texture_offset' : Vec2(0.0, 0.0),
    'point_size' : 1.0,

    'perspective_scaling': True,
},
continuous_input = {
    'window_size': Func(getattr, window, 'size'),
    }
)


if __name__ == '__main__':
    from ursina import *
    from ursina.prefabs.primitives import *
    app = Ursina(vsync=1)
    camera.clip_plane_near= 1
    # window.color=color.black
    Entity(model='plane', scale=10, texture='grass')

    vertices=[Vec3(*(random.random()*10 for _ in range(3))) for i in range(100)]
    e = Entity(model=Mesh(mode=MeshModes.point, vertices=vertices, colors=[color.random_color() for _ in vertices], render_points_in_3d=True, thickness=50), shader=unlit_points_shader
    , texture='circle'
    )

    slider = ThinSlider(text='point_size', min=1, max=32, default=4)
    def _set_point_size():
        e.set_shader_input('point_size', slider.value)
        print('set point_size to:', slider.value, e.get_shader_input('point_size'))
    slider.on_value_changed = _set_point_size

    EditorCamera()
    app.run()
