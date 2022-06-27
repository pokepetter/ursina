from ursina import *

texture_blend_shader = Shader(name='texture_blend_shader', language=Shader.GLSL, 
fragment='''
#version 430

in vec2 uv;
out vec4 color;

uniform sampler2D red_texture;
uniform sampler2D green_texture;
uniform sampler2D blue_texture;

uniform sampler2D blend_map;

uniform vec2 red_uv;
uniform vec2 green_uv;
uniform vec2 blue_uv;

uniform vec4 red_tint;
uniform vec4 green_tint;
uniform vec4 blue_tint;

vec4 blend(vec4 texture1, float a1, vec4 texture2, float a2) {
    float depth = 0.1;
    float ma = max(texture1.a + a1, texture2.a + a2) - depth;

    float b1 = max(texture1.a + a1 - ma, 0);
    float b2 = max(texture2.a + a2 - ma, 0);

    return (texture1.rgba * b1 + texture2.rgba * b2) / (b1 + b2);
}

void main() {
    vec4 map = texture(blend_map, uv);

    vec4 tex0 = texture(red_texture, uv*red_uv*vec2(16,16)).rgba * red_tint;
    vec4 tex1 = texture(green_texture, uv*green_uv*vec2(16,16)).rgba * green_tint;
    vec4 tex2 = texture(blue_texture, uv*blue_uv*vec2(12,12)).rgba * blue_tint;

    vec4 final = blend(tex0, map.r, tex2, map.b);
    final = blend(final, max(map.r, map.b), tex1, map.g);
    color = vec4(final.rgb, 1.0);
    //color = vec4(tex2.a, tex2.a, tex2.a, 1.0);
}

''',

default_input = {
    'red_tint' : color.white,
    'green_tint' : color.white,
    'blue_tint' : color.white,
    'red_uv' : Vec2(1,1),
    'green_uv' : Vec2(1,1),
    'blue_uv' : Vec2(2.0, 2.0),
}
)

if __name__ == '__main__':
    from ursina import *
    Texture.default_filtering = 'bilinear'
    app = Ursina(vsync=False)

    e = Entity(model='plane', shader=texture_blend_shader, texture='shore')
    e.set_shader_input('red_texture', load_texture('dirt'))
    e.set_shader_input('green_texture', load_texture('grass_tintable.tif'))
    e.set_shader_input('green_tint', color.hex('#6f6d24'))
    # e.set_shader_input('green_tint', color.hsv(78,59,50))
    e.set_shader_input('blue_texture', load_texture('cobblestone.tif'))
    blend_map = load_texture('texture_blend_map_example')
    e.set_shader_input('blend_map', blend_map)
    e.scale_x = blend_map.width / blend_map.height
    e.scale *= 200
    # e.set_shader_input('red_tint', color.black)
    # e.set_shader_input('green_tint', color.lime)
    # e.set_shader_input('blue_tint', color.white)

    # e.set_shader_input('blue_uv', Vec2(4,4))

    EditorCamera(rotation_x=30)

    def input(key):
        if key == 'space':
            if e.shader:
                e.shader = None
            else:
                e.shader = texture_blend_shader

        if key == 'left mouse up':
            blend_map.apply()


    e.collider = 'mesh'
    #e.shader = None
    #e.texture = blend_map
    def update():
        if mouse.left and mouse.hovered_entity == e:
            x, _, y = mouse.point + Vec3(.5)
            print(x, y)
            blend_map.set_pixel(int(x*blend_map.width), int(y*blend_map.height), color.green)
            blend_map.apply()


    app.run()
