from panda3d.core import Shader as Panda3dShader

default_vertex_shader = '''
#version 130
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  texcoord = p3d_MultiTexCoord0;
'''

class Shader:
    CG = Panda3dShader.SL_Cg
    GLSL = Panda3dShader.SL_GLSL
    HLSL = Panda3dShader.SL_HLSL
    SPIR_V = Panda3dShader.SL_SPIR_V

    def __init__(self, language=Panda3dShader.SL_GLSL, vertex=default_vertex_shader, fragment='', geometry='', **kwargs):

        self._shader = Panda3dShader.make(language, vertex, fragment, geometry)
        self.entity = None
        self.default_input = dict()

        for key, value in kwargs.items():
            setattr(self, key ,value)
