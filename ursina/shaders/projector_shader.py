from ursina import *; projector_shader = Shader(language=Shader.GLSL, vertex = '''
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 texcoord;
uniform vec2 projector_uv_scale;

out vec2 world_uv;
uniform float time;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = p3d_MultiTexCoord0;
    world_uv = (p3d_ModelMatrix * p3d_Vertex).xz * projector_uv_scale;
    // world_uv += vec2(time, time);
}
''',

fragment='''
#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoord;
out vec4 fragColor;

uniform sampler2D projector_texture;
in vec2 world_uv;
//uniform float t;


void main() {
    vec4 color = texture(p3d_Texture0, texcoord) * p3d_ColorScale;
    color.rgb -= texture(projector_texture, world_uv).r * .2;
    fragColor = color.rgba;
}''',

default_input = {
    'projector_texture' : Func(load_texture, 'noise'),
    'projector_uv_scale' : Vec2(.1, .1),
    'time' : 0.0,
}
)


if __name__ == '__main__':
    from ursina import *
    Texture.default_filtering = 'bilinear'
    app = Ursina()

    e = Draggable(parent=scene, color=color.white, plane_direction=Vec3(0,1,0), model='cube', texture='brick', shader=projector_shader)
    ground = Entity(model='plane', scale=32, texture='grass', shader=projector_shader)
    t = Entity(model='quad', texture='noise', x=1000).texture
    editor_camera = EditorCamera(rotation_x=30,)

    ground.t = 0

    def update():
        ground.t += time.dt
        ground.set_shader_input('time', ground.t)


    app.run()
