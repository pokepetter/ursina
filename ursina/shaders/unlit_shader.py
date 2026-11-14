import ursina
from ursina.ursinastuff import Func
from ursina.shader import Shader
from ursina.vec2 import Vec2
from ursina.vec3 import Vec3
from ursina import color
# from ursina.camera import instance as camera
# from ursina.scene import instance as scene
base_shader = Shader(name='base_shader', language=Shader.GLSL, vertex='''\
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
''',
fragment='''\
#version 140
out vec4 frag_color;
void main() {
    frag_color = vec4(1.,1.,1.,1.);
}
''',
)


color_shader = Shader(name='color_shader', language=Shader.GLSL,
vertex=base_shader.vertex,
fragment='''\
#version 140
uniform vec4 p3d_ColorScale;
out vec4 frag_color;

void main() {
    frag_color = p3d_ColorScale;
}
''',

)

vertex_color_pass = Shader(name='vertex_color_pass', language=Shader.GLSL, vertex = '''\
#version 140
in vec4 p3d_Color;
out vec4 vertex_color;

void main() {
    vertex_color = p3d_Color;
}
''',

fragment='''\
#version 140
in vec4 vertex_color;
out vec4 frag_color;

void main() {
    frag_color *= vertex_color;
}
''',
)

texture_pass = Shader(name='texture_pass', language=Shader.GLSL, vertex = '''\
#version 140
in vec2 p3d_MultiTexCoord0;
out vec2 uvs;
uniform vec2 texture_scale;
uniform vec2 texture_offset;

void main() {
    uvs = (p3d_MultiTexCoord0 * texture_scale) + texture_offset;
}
''',
fragment='''\
#version 140
in vec4 vertex_color;
out vec4 frag_color;
uniform sampler2D p3d_Texture0;
in vec2 uvs;

void main() {
    frag_color *= texture(p3d_Texture0, uvs);
}
''',
default_input={
    'texture_scale': Vec2(1,1),
    'texture_offset': Vec2(0.0, 0.0),
},
)

textureless_shader = base_shader + color_shader + vertex_color_pass
textureless_shader.name = 'textureless_shader'
textureless_shader.compile()

unlit_shader = base_shader + color_shader + vertex_color_pass + texture_pass
unlit_shader.name = 'unlit_shader'
unlit_shader.compile()
# print(unlit_shader.vertex, unlit_shader.fragment)

if __name__ == '__main__':
    from ursina import EditorCamera, Entity, Ursina, load_model, Text
    app = Ursina()

    ground = Entity(model='plane', color=color.gray, scale=10, y=-2, texture='shore', shader=unlit_shader, texture_scale=(10,10))
    ground.set_shader_input('texture_scale', Vec2(2, 1))

    for i, shader in enumerate((base_shader, color_shader, textureless_shader, unlit_shader)):
        e = Entity(model=load_model('cube', use_deepcopy=True), x=i*1.5, shader=shader, texture='shore', color=color.blue)
        Text(parent=e, y=1, text=shader.name)
        e.model.colors = [color.random_color() for v in e.model.vertices]
        e.model.generate()
    #Sky(color=color.light_gray)
    EditorCamera()

    app.run()
