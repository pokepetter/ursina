from ursina import color
from ursina.shader import Shader
from ursina.vec3 import Vec3

toon_shader = Shader(name='toon_shader', language=Shader.GLSL, vertex = '''#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 texcoord;

in vec3 p3d_Normal;
out vec3 world_normal;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = p3d_MultiTexCoord0;
    world_normal = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);
}
''',
fragment='''
#version 120

uniform vec3 lightDir;
varying vec3 world_normal;

void main() {
    float intensity;
    vec4 color;

    intensity = dot(lightDir, world_normal);
    if (intensity > 0.95) color = vec4(1.0, 0.5, 0.5, 1.0);
    else if (intensity > 0.5) color = vec4(0.6, 0.3, 0.3, 1.0);
    else if (intensity > 0.25) color = vec4(0.4, 0.2, 0.2, 1.0);
    else color = vec4(0.2, 0.1, 0.1, 1.0);

    gl_FragColor = color;
}
''',
default_input={
    # 'texture_scale' : Vec2(1,1),
    # 'texture_offset' : Vec2(0.0, 0.0),
    'lightDir' : Vec3(1,-1,1)
}
)


if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    shader = toon_shader
    e = Entity(model='sphere', y=2, color=color.azure, shader=shader)
    e.model.generate_normals(smooth=True)
    Entity(model='plane', scale=8, shader=shader)
    EditorCamera()
    def update():
        if held_keys["d"]: e.rotation_y += 4
        if held_keys["a"]: e.rotation_y -= 4
    app.run()
