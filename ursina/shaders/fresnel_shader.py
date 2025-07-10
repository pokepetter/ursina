from ursina import camera, color, load_texture
from ursina.shader import Shader
from ursina.ursinastuff import Func
from ursina.vec2 import Vec2

fresnel_shader = Shader(name='fresnel_shader', language=Shader.GLSL,
vertex = '''
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 texcoord;
uniform vec2 texture_scale;
uniform vec2 texture_offset;

in vec3 p3d_Normal;
out vec3 world_normal;
out vec3 world_position;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = (p3d_MultiTexCoord0 * texture_scale) + texture_offset;
    world_normal = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);
    world_position = mat3(p3d_ModelMatrix) * p3d_Vertex.xyz;
}
''',

fragment='''
#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoord;
in vec3 world_normal;
in vec3 world_position;
out vec4 fragColor;

uniform vec4 fresnel_color;
uniform sampler2D fresnel_texture;
uniform vec3 camera_world_position;
uniform float bias;
uniform float scale;
uniform float power;

vec3 do_fresnel(vec4 color) {
    vec3 offset_camera_world_position = camera_world_position + vec3(0.,0.,-1.);
    vec3 I = normalize(world_position - offset_camera_world_position.xyz);
    float fresnel = bias + scale * pow(1.0 + dot(I, world_normal), power);

    fresnel *= texture(fresnel_texture, texcoord).r;
    return mix(color.rgb, fresnel_color.rgb, fresnel*fresnel_color.a);
}

void main() {
    vec4 color = texture(p3d_Texture0, texcoord) * p3d_ColorScale;

    fragColor.rgb = do_fresnel(color);
    fragColor.a = color.a;
}


''', geometry='',
default_input = {
    'texture_scale' : Vec2(1,1),
    'texture_offset' : Vec2(0.0, 0.0),

    'fresnel_color' : color.light_gray,
    'fresnel_texture' : Func(load_texture, 'white_cube'),
    'bias' : .05,
    'scale' : 1,
    'power' : 2.0,
    'camera_world_position': Func(getattr, camera, 'world_position'),
},
continuous_input = {
    'camera_world_position': Func(getattr, camera, 'world_position'),
    }
)



if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    # window.color=color.black

    b = Entity(model='sphere', color=color.black, shader=fresnel_shader)
    b = Entity(model=Quad(), color=color.dark_gray, shader=fresnel_shader, x=.25, parent=camera.ui, scale=.2, ignore=True)
    b.shader_input = {
        'bias': .01,
        'scale': 1.5,
        'power': 1.5,
        'fresnel_color': color.hex('#123123')
    }
    b.animate_rotation_y(15, duration=1, curve=curve.linear_boomerang, loop=True)
    ground = Entity(model='plane', color=color.gray, shader=fresnel_shader, y=-1, scale=64, texture='grass', texture_scale=Vec2(32,32))
    ground.set_shader_input('fresnel_color', color.gray)
    ground.set_shader_input('fresnel_texture', load_texture('white_cube'))
    EditorCamera()

    app.run()
