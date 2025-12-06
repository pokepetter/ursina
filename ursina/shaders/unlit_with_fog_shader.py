import ursina
from ursina import color
from ursina.scene import instance as scene
from ursina.shader import Shader
from ursina.ursinastuff import Func
from ursina.vec2 import Vec2
from ursina.vec3 import Vec3

unlit_with_fog_shader = Shader(name='unlit_shader', language=Shader.GLSL, vertex = '''\
#version 130
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 uvs;
uniform vec2 texture_scale;
uniform vec2 texture_offset;

in vec4 p3d_Color;
out vec4 vertex_color;
out vec3 vertex_world_position;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uvs = (p3d_MultiTexCoord0 * texture_scale) + texture_offset;
    vertex_color = p3d_Color;
    vertex_world_position = (p3d_ModelMatrix * p3d_Vertex).xyz;
}
''',

fragment='''
#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 uvs;
out vec4 color;

in vec4 vertex_color;
in vec3 vertex_world_position;
uniform vec3 camera_world_position;
uniform vec4 fog_color;
uniform float fog_start;
uniform float fog_end;

void main() {
    color = texture(p3d_Texture0, uvs) * p3d_ColorScale * vertex_color;
    float distance_to_camera = length(vertex_world_position.xyz - camera_world_position);
    float fog_length = fog_end - fog_start;
    float t = distance_to_camera/fog_length;
    t = clamp(t, 0., 1.);
    color.rgb = mix(color.rgb, fog_color.rgb, t * fog_color.a);
}

''',
default_input={
    'texture_scale': Vec2(1,1),
    'texture_offset': Vec2(0.0, 0.0),
    'fog_color': color.clear,
    'fog_start': 10,
    'fog_end': 100,
    'camera_world_position' : Vec3.zero,
},
)
def get_camera_world_position():
    from ursina import camera
    return camera.world_position
unlit_with_fog_shader.continuous_input['camera_world_position'] = get_camera_world_position



if __name__ == '__main__':
    from ursina import EditorCamera, Entity, Ursina, camera
    app = Ursina()
    # window.color=color.black
    # from ursina.lights import DirectionalLight
    # DirectionalLight()

    shader = unlit_with_fog_shader

    a = Entity(model='cube', shader=shader)
    # b = YellowSphere(shader=shader, rotation_y=180, x=3, texture='shore')
    # from panda3d.core import Material
    # myMaterial = Material()
    # myMaterial.setShininess(5.0) #Make this material shiny
    # myMaterial.setAmbient((0, 0, 1, 1)) #Make this material blue
    # b.set_material(myMaterial)
    # AzureSphere(shader=a.shader, y=2)
    ground = Entity(model='plane', color=color.gray, scale=10, y=-2, texture='shore', shader=shader, texture_scale=(10,10))
    ground.set_shader_input('texture_scale', Vec2(2, 1))
    #Sky(color=color.light_gray)
    EditorCamera()

    scene.fog_color = color.blue
    scene.fog_density = (0, 100)

    # def input(key):
    #     if key == 'b':
    #         unlit_with_fog_shader.fog_color = color.blue

    app.run()
