from ursina import *
from panda3d.core import Shader as Panda3dShader


colored_lights_shader = Shader(name='colored_lights_shader', language=Shader.GLSL, 
vertex='''
#version 130
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;

out vec2 texcoord;
out vec3 world_normal;
out vec4 vertex_color;


void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  world_normal = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);
  vertex_color = p3d_Color;
}
''',

fragment='''
#version 130

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoord;
in vec3 world_normal;
in vec4 vertex_color;

uniform vec4 top_color;
uniform vec4 bottom_color;
uniform vec4 left_color;
uniform vec4 right_color;
uniform vec4 front_color;
uniform vec4 back_color;

out vec4 fragColor;


void main() {
    vec4 norm = vec4(world_normal*0.5+0.5, 1);
    vec4 color = texture(p3d_Texture0, texcoord) * vertex_color * p3d_ColorScale;
    // color += mix(bottom_color, top_color, norm.y) / 3.;
    // color += mix(right_color, left_color, norm.x) / 3.;
    // color += mix(front_color, back_color, norm.z) / 3.;
    color *= mix(bottom_color, top_color, norm.y);
    color *= mix(left_color, right_color, norm.x) * 1.5;
    color *= mix(front_color, back_color, norm.z) * 2.;
    // vec3 target_col = vec3(
    //     mix(right_color, left_color, norm.x),
    //     mix(bottom_color, top_color, norm.y),
    //     mix(front_color, back_color, norm.z)
    // );

    // color.rgb -= vec3(.5,.5,.5);
    // color.rgb = mix(color, target_col, .5);
    color = mix(color, vec4(1), 0.1);
    color *= 1.25;
    fragColor = vec4(color.rgb, 1.);
    // fragColor = vec4(vcol.rgb, 1.);
}


''',
geometry='',
default_input = {
    'top_color': color.color(220, .12, .82),
    'bottom_color': color.color(285, .13, .47),
    'left_color': color.color(217, .3, .68),
    'right_color': color.color(0, .25, .93),
    'front_color': color.color(231, .08, .69),
    'back_color': color.color(240, .05, .76),
    }
)


if __name__ == '__main__':
    from ursina import *
    from ursina.prefabs.primitives import *
    app = Ursina()
    window.color=color.black

    # e = Entity(model='sphere', shader=basic_lighting_shader)
    shader = colored_lights_shader

    Entity(model='cube', color=color.white, shader=colored_lights_shader)
    e = Entity(model='cube', x=1.2, shader=colored_lights_shader)
    e.model.colors = len(e.model.vertices) * (color.red, )
    e.model.generate()
    # AzureSphere(shader=a.shader, y=2)
    GrayPlane(scale=10, y=-2, texture='shore')

    Sky(color=color.light_gray)
    EditorCamera(rotate_around_mouse_hit=False)


    EditorCamera()

    app.run()
