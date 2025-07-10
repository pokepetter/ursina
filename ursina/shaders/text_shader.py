'''
SDF text shader based on: https://github.com/wezu/sdf_text
License: Copyright (c) 2018, wezu (wezu.dev@gmail.com)

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
'''

from ursina import color
from ursina.shader import Shader
from ursina.vec2 import Vec2

text_shader = Shader(name='text_shader', language=Shader.GLSL,
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
in vec2 uvs;
out vec4 FINAL_COLOR;

in vec4 vertex_color;

void main() {
    float dist = texture(p3d_Texture0, uvs).a;
    vec2 width = vec2(0.5-fwidth(dist), 0.5+fwidth(dist));
    float alpha = smoothstep(width.x, width.y, dist);
    //supersampling
    float scale = 0.354; // half of 1/sqrt2 - value from internet(???)
    vec2 duv = scale * (dFdx(uvs) + dFdy(uvs));
    vec4 box = vec4(uvs-duv, uvs+duv);
    alpha +=0.5*(smoothstep(width.x, width.y, texture(p3d_Texture0, box.xy).a)
            +smoothstep(width.x, width.y, texture(p3d_Texture0, box.zw).a)
            +smoothstep(width.x, width.y, texture(p3d_Texture0, box.xw).a)
            +smoothstep(width.x, width.y, texture(p3d_Texture0, box.zy).a));
    alpha /= 3.0; //weighted average, 1*1 + 4*0.5 = 3, so divide by 3
    //outline
    float outline = pow(texture(p3d_Texture0, uvs-outline_offset).a, outline_power);
    FINAL_COLOR = mix(vec4(vertex_color.rgb, outline_color.a * outline), vertex_color, alpha);
}
''',

default_input = {
    'outline_color': color.white,
    'outline_offset': Vec2(10,10),
    'outline_power': 1.0,
}
)

if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    # window.color = color._16

    text_entity = Text('some <orange>COOL <default> text here', parent=scene, scale=25)
    text_shader.compile()

    for tn in text_entity.text_nodes:
        tn.setShader(text_shader._shader)
        for key, value in text_shader.default_input.items():
            tn.setShaderInput(key, value)
            print(tn.getColorScale())

    EditorCamera()

    app.run()
