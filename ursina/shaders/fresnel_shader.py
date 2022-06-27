from ursina import *


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

vec3 do_fresnel(vec4 color) {
    float _Bias = .05;
    float _Scale = .5;
    float _Power = 3.0;
    vec3 I = normalize(world_position - camera_world_position.xyz);
    float fresnel = _Bias + _Scale * pow(1.0 + dot(I, world_normal), _Power);

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
}
)


if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    # window.color=color.black

    b = Entity(model='sphere', color=color.black, shader=fresnel_shader)
    ground = Entity(model='plane', color=color.gray, shader=fresnel_shader, y=-1, scale=64, texture='grass', texture_scale=Vec2(32,32))
    ground.set_shader_input('fresnel_color', color.gray)
    ground.set_shader_input('fresnel_texture', load_texture('white_cube'))
    EditorCamera()

    for i in range(16):
        e = Entity(model='cube', origin_y=-.5, scale=2, texture='brick', texture_scale=(1,2),
            x=random.uniform(-8,8),
            z=random.uniform(-8,8) + 8,
            # collider='box',
            scale_y = random.uniform(2,3),
            color=color.hsv(0, 0, random.uniform(.9, 1)),
            shader=fresnel_shader,
            )
        e.set_shader_input('fresnel_texture', load_texture('brick'))

    def update():
        for e in scene.entities:
            if hasattr(e, 'shader') and e.shader == fresnel_shader:
                e.set_shader_input('camera_world_position', camera.world_position)


        # ground.set_shader_input('camera_world_position', camera.world_position)


    # def update():
    #     b.rotation_y += 1
    #     #b.rotation_z += 1
    #     b.rotation_x += 1
    #     b.set_shader_input('transform_matrix', b.getNetTransform().getMat())
    # EditorCamera()

    app.run()
