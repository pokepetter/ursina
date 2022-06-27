from ursina import *; projector_shader = Shader(name='projector_shader', language=Shader.GLSL, vertex = '''
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
uniform vec2 texture_scale;
uniform vec2 texture_offset;
out vec2 texcoord;
uniform vec2 projector_uv_scale;
uniform vec2 projector_uv_offset;

out vec2 world_uv;
uniform float time;

out float z;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = (p3d_MultiTexCoord0 * texture_scale) + texture_offset;
    world_uv = (p3d_ModelMatrix * p3d_Vertex).xz * projector_uv_scale;
    world_uv -= projector_uv_offset;
    world_uv += vec2(.5);
    z = gl_Position.z;
}
''',

fragment='''
#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoord;
out vec4 fragColor;

uniform sampler2D projector_texture;
uniform vec4 projector_color;
in vec2 world_uv;

uniform struct p3d_FogParameters {
  vec4 color;
  float density;
  float start;
  float end;
  float scale; // 1.0 / (end - start)
} p3d_Fog;

in float z;

float inverse_lerp(float a, float b, float v) {
    return (v-a) / (b-a);
}

void main() {
    vec4 color = texture(p3d_Texture0, texcoord) * p3d_ColorScale;
    color.rgb -= texture(projector_texture, world_uv).r * (vec3(1.) - projector_color.rgb) * projector_color.a;
    color.rgb = mix(color.rgb, p3d_Fog.color.rgb, clamp(inverse_lerp(p3d_Fog.start, p3d_Fog.end, z), 0.0, 1.0)); // linear fog

    fragColor = color.rgba;
}''',

default_input = {
    'texture_scale': Vec2(1,1),
    'texture_offset': Vec2(0,0),
    'projector_texture' : Func(load_texture, 'vignette'),
    'projector_uv_scale' : Vec2(.05, .05),
    'projector_uv_offset' : Vec2(.0, .0),
    'projector_color' : color.black,
    'time' : 0.0,
}
)


if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    Entity.default_shader = projector_shader

    editor_camera = EditorCamera(rotation_x=30,)
    light = Entity(model='sphere', unlit=True)
    ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4))

    random.seed(0)
    for i in range(16):
        Entity(model='cube', origin_y=-.5, scale=2, texture='brick', texture_scale=(1,2),
            x=random.uniform(-8,8),
            z=random.uniform(-8,8) + 8,
            collider='box',
            scale_y = random.uniform(2,3),
            color=color.hsv(0, 0, random.uniform(.9, 1))
        )

    scene.fog_density = (10, 200)

    projector_texture = load_texture('vignette', application.internal_textures_folder)
    # projector_texture.repeat = False
    projector_shader.default_input['projector_texture'] = projector_texture

    def update():
        light.x += (held_keys['d'] - held_keys['a']) * time.dt * 3
        light.z += (held_keys['w'] - held_keys['s']) * time.dt * 3

        for e in scene.entities:
            if hasattr(e,'shader') and e.shader == projector_shader:
                e.set_shader_input('projector_uv_offset', light.world_position.xz * projector_shader.default_input['projector_uv_scale'])

    app.run()
