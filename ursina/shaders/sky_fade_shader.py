from ursina import camera, color
from ursina.shader import Shader
from ursina.ursinastuff import Func
from ursina.vec2 import Vec2
from ursina.vec3 import Vec3

sky_fade_shader = Shader(name='sky_fade_shader', language=Shader.GLSL, vertex='''
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec4 p3d_Color;
out vec3 world_normal;
out vec3 vertex_world_position;
out vec2 texcoord;
out vec4 vertex_color;

uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p3d_ModelMatrix;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = p3d_MultiTexCoord0;

    world_normal = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);
    vertex_world_position = (p3d_ModelMatrix * p3d_Vertex).xyz;
    vertex_color = p3d_Color;

}

''',

fragment='''
#version 150

uniform vec4 p3d_ColorScale;
in vec2 texcoord;
out vec4 fragment_color;

uniform sampler2D p3d_Texture0;
in vec3 world_normal;
in vec3 vertex_world_position;

uniform vec2 texture_scale;

in vec4 vertex_color;
uniform vec3 camera_world_position;

uniform vec4 top_color;
uniform vec4 bottom_color;
uniform vec4 left_color;
uniform vec4 right_color;
uniform vec4 front_color;
uniform vec4 back_color;

uniform sampler2D heightmap;
uniform sampler2D sky_texture;
const float M_PI = 3.14159265358979323846;
uniform float fog_start = 20.;
uniform float fog_end = 200.;


vec4 sky_colored_fog(vec4 color, vec3 vertex_world_position) {
    float distance_to_camera = length(vertex_world_position.xyz - camera_world_position);

    vec3 new_color = color.rgb;

    vec3 vertex_relative_position = vertex_world_position - camera_world_position;
    //vertex_relative_position = vertex_world_position;

    vec2 direction = normalize(vertex_relative_position.zx);
    float angle = atan(direction.y, direction.x); // angle in radians
    float circle_point = clamp(mod((angle / (2.0 * M_PI)) + 1.0, 1.0), 0., 1.);

    vec2 vertical_direction = normalize(vertex_relative_position.yz);
    float vertical_angle = atan(vertical_direction.y, vertical_direction.x); // angle in radians
    float vertical_circle_point = clamp(mod((vertical_angle / (2.0 * M_PI)) + 1.0, 1.0), 0.0, 1.0);

    float y = .1;
    vec4 fog_color = texture(sky_texture, vec2(circle_point, y));
    float offset = .05;
    // fog_color = (
    //     texture(sky_texture, vec2(circle_point, y)).rgb
    //     + texture(sky_texture, vec2(circle_point-offset, y-offset)).rgb
    //     + texture(sky_texture, vec2(circle_point+offset, y-offset)).rgb
    //     + texture(sky_texture, vec2(circle_point-offset, y+offset)).rgb
    //     + texture(sky_texture, vec2(circle_point+offset, y+offset)).rgb
    //     ) / 5.;

    // fog_color = texture(sky_texture, vec2(circle_point, vertical_circle_point)).rgb;
    // float offset = .05;
    // fog_color = (
    //     texture(sky_texture, vec2(circle_point, vertical_circle_point)).rgb
    //     + texture(sky_texture, vec2(circle_point-offset, vertical_circle_point-offset)).rgb
    //     + texture(sky_texture, vec2(circle_point+offset, vertical_circle_point-offset)).rgb
    //     + texture(sky_texture, vec2(circle_point-offset, vertical_circle_point+offset)).rgb
    //     + texture(sky_texture, vec2(circle_point+offset, vertical_circle_point+offset)).rgb
    //     ) / 5.;



    float distance_from_center = length(vertex_relative_position.xz);
    float t = clamp((distance_from_center - fog_start) / (fog_end - fog_start), 0.0, 1.0);
    color.rgb = mix(color.rgb, fog_color.rgb, t * fog_color.a);
    return color;
}

void main(){
    vec4 vert_color = mix(bottom_color, top_color, world_normal.y);
    vert_color *= mix(left_color, right_color, world_normal.x) * 1.5;
    vert_color *= mix(front_color, back_color, world_normal.z) * 2.;
    vert_color = mix(vert_color, vec4(1), 0.1);
    vert_color *= 1.25;

    fragment_color = texture(p3d_Texture0, texcoord) * p3d_ColorScale * vert_color;
    fragment_color = sky_colored_fog(fragment_color, vertex_world_position);
}

''',
default_input = {
    'texture_scale' : Vec2(.1, .1),

    'top_color': color.hsv(220, .12, .82),
    'bottom_color': color.hsv(285, .13, .47),
    'left_color': color.hsv(217, .3, .68),
    'right_color': color.hsv(0, .25, .93),
    'front_color': color.hsv(231, .08, .69),
    'back_color': color.hsv(240, .05, .76),

    'sky_texture': 'sky_default',
    'camera_world_position' : Vec3.zero,
    'fog_start': 50,
    'fog_end': 1000,
    }
,
continuous_input = {
    'camera_world_position': Func(getattr, camera, 'world_position'),
    }
)

if __name__ == '__main__':
    import random

    from ursina import Entity, Sky, Ursina
    from ursina.prefabs.first_person_controller import FirstPersonController
    app = Ursina()
    FirstPersonController(gravity=0)
    # camera.z = -200
    # EditorCamera(rotation_x=60)
    sky = Sky(texture='sky_sunset')
    e = Entity(model='plane', scale=(2000,1,2000), texture='grass', shader=sky_fade_shader)
    e.set_shader_input('sky_texture', sky.texture)
    for i in range(100):
        Entity(model='cube', scale=(25,random.randint(10,150),25), x=-1000+(random.random()*2000), z=-1000+(random.random()*2000), origin_y=-.5, shader=sky_fade_shader, shader_input=dict(sky_texture=sky.texture))
    # camera.fov = 100
    # camera.clip_plane_far = 1000
    print('-----------', camera.clip_plane_far)
    app.run()