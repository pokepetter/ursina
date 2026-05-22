from ursina import color
from ursina.shader import Shader
from ursina.vec2 import Vec2

text_with_shadows_shader = Shader(name='text_with_shadows_shader', language=Shader.GLSL,
vertex='''#version 130

uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 uvs;

in vec4 p3d_Color;
out vec4 vertex_color;


void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uvs = p3d_MultiTexCoord0;
    vertex_color = p3d_Color;
}
''',

fragment='''
#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
uniform vec4 outline_color;
uniform vec2 outline_offset;
uniform float outline_power;
uniform vec2 shadow_offset;
uniform vec4 shadow_color;
in vec2 uvs;
in vec4 vertex_color;
out vec4 FINAL_COLOR;

void main() {
    float dist = texture(p3d_Texture0, uvs).a;
    vec2 width = vec2(0.5-fwidth(dist), 0.5+fwidth(dist));
    float alpha = smoothstep(width.x, width.y, dist);

    float shadow_alpha = texture(p3d_Texture0, uvs - shadow_offset).a;
    vec4 shadow_col = vec4(shadow_color.rgb, shadow_color.a * shadow_alpha);
    vec4 text_col = vec4(vertex_color.rgb, vertex_color.a * alpha);

    vec4 col = shadow_col;
    col.rgb = mix(col.rgb, text_col.rgb, alpha);
    col.a = max(shadow_col.a, text_col.a);

    FINAL_COLOR = col * p3d_ColorScale * vertex_color;
}
''',

default_input = {
    'outline_color': color.white,
    'outline_offset': Vec2(10,10),
    'outline_power': 1.0,
    'shadow_color': color.hex('#190b39'),
    'shadow_offset': Vec2(0.01, -0.01),
}
)

text_with_shadows_shader.compile()
if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    # window.color = color._16

    text_entity = Text('some <orange>COOL <default> text here', parent=scene, scale=25, shader=text_with_shadows_shader)

    def input(key):
        if key == 'f':
            text_entity.fade_out()


    EditorCamera()

    app.run()
