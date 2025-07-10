from ursina import color
from ursina.shader import Shader
from ursina.vec2 import Vec2

unlit_shader = Shader(name='unlit_shader', language=Shader.GLSL, vertex = '''#version 130


uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 uvs;
uniform vec2 texture_scale;
uniform vec2 texture_offset;

in vec4 p3d_Color;
out vec4 vertex_color;


void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uvs = (p3d_MultiTexCoord0 * texture_scale) + texture_offset;
    vertex_color = p3d_Color;
}
''',

fragment='''
#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 uvs;
out vec4 fragColor;

in vec4 vertex_color;

void main() {
    //// for point support use gl_PointCoord instead of p3d_MultiTexCoord0
    //vec2 pointUV = gl_PointCoord;  // Use built-in point sprite UVs
    //vec4 texColor = texture(p3d_Texture0, pointUV);  // Sample the texture

    vec4 color = texture(p3d_Texture0, uvs) * p3d_ColorScale * vertex_color;
    fragColor = color.rgba;
}

''',
default_input={
    'texture_scale' : Vec2(1,1),
    'texture_offset' : Vec2(0.0, 0.0),
}
)



if __name__ == '__main__':
    from ursina import EditorCamera, Entity, Ursina
    app = Ursina()
    # window.color=color.black
    # from ursina.lights import DirectionalLight
    # DirectionalLight()

    shader = unlit_shader

    # a = AzureCube(shader=shader)
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

    app.run()
