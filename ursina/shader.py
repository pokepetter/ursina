from pathlib import Path
from panda3d.core import Shader as Panda3dShader
from ursina import application

default_vertex_shader = '''
#version 430
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 uv;

void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  uv = p3d_MultiTexCoord0;
}
'''

default_fragment_shader='''
#version 430

uniform sampler2D tex;
in vec2 uv;
out vec4 color;

void main() {
    vec3 rgb = texture(tex, uv).rgb;
    color = vec4(rgb, 1.0);
}

'''

class Shader:
    CG = Panda3dShader.SL_Cg
    GLSL = Panda3dShader.SL_GLSL
    HLSL = Panda3dShader.SL_HLSL
    SPIR_V = Panda3dShader.SL_SPIR_V

    def __init__(self, language=Panda3dShader.SL_GLSL, vertex=default_vertex_shader, fragment=default_fragment_shader, geometry='', **kwargs):

        self._shader = Panda3dShader.make(language, vertex, fragment, geometry)
        self.entity = None
        self.default_input = dict()

        for key, value in kwargs.items():
            setattr(self, key ,value)

    @classmethod
    def load(cls, language=Panda3dShader.SL_GLSL, vertex=None, fragment=None, geometry=None, **kwargs):
        parts = {"vertex": vertex, "fragment": fragment, "geometry": geometry}
        parts = {k: v for k, v in parts.items() if v}

        folders = (  # folder search order
            application.asset_folder,
        )

        for sh, name in parts.items():
            for folder in folders:
                for filename in folder.glob('**/' + name):
                    with filename.open("rt") as f:
                        parts[sh] = f.read()

        parts.update(kwargs)
        return cls(language, **parts)


if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    Entity(model='cube', shader=Shader())
    EditorCamera()
    app.run()
