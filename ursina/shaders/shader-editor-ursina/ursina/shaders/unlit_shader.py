from ursina import *; unlit_shader = Shader(name='unlit_shader', language=Shader.GLSL, vertex = '''#version 130


uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 texcoords;
uniform vec2 texture_scale;
uniform vec2 texture_offset;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoords = (p3d_MultiTexCoord0 * texture_scale) + texture_offset;
}
''',

fragment='''
#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoords;
out vec4 fragColor;

void main() {
    vec4 color = texture(p3d_Texture0, texcoords) * p3d_ColorScale;
    fragColor = color.rgba;
}

''',
default_input={
    'texture_scale' : Vec2(1,1),
    'texture_offset' : Vec2(0.0, 0.0),
}
)



if __name__ == '__main__':
    from ursina import *
    from ursina.prefabs.primitives import *
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
    ground = GrayPlane(scale=10, y=-2, texture='shore', shader=shader, texture_scale=(10,10))
    ground.set_shader_input('texture_scale', Vec2(2, 1))
    #Sky(color=color.light_gray)
    EditorCamera()

    app.run()
