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
imported_shaders = dict()

def do_shader_includes(shader_source, included=None):
    if shader_source is None:
        return None
    if shader_source == "":
        return ""
    inc = None
    if included is not None:
        inc = included
    else:
        inc = set()
    lines = shader_source.split("\n")
    res = ""
    for line in lines:
        if line.startswith("#include"):
            str_start = line.find("\"")
            include_str = line[str_start:]
            str_end = include_str[1:].find("\"")
            if str_end == -1:
                raise Exception("Missing closing quotation mark in GLSL include.")
            include_path = include_str[1:-1]
            include_path = include_path.replace("ursina/", str(application.package_folder / "shaders") + "/")
            if include_path not in inc:
                inc.add(include_path)
                with open(include_path, "r") as f:
                    file_contents = f.read() + "\n"
                    file_contents = do_shader_includes(file_contents, included=inc)
                    res += file_contents
        else:
            res += line + "\n"
    return res

class Shader:
    CG = Panda3dShader.SL_Cg
    GLSL = Panda3dShader.SL_GLSL
    HLSL = Panda3dShader.SL_HLSL
    SPIR_V = Panda3dShader.SL_SPIR_V

    def __init__(self, name='untitled_shader', language=GLSL, vertex=default_vertex_shader, fragment=default_fragment_shader, geometry='', **kwargs):

        if not ('__compiled__' in globals() and str(globals()['__compiled__'].__class__.__name__) == '__nuitka_version__'):
            from inspect import getframeinfo, stack
            _stack = stack()
            _caller = getframeinfo(_stack[1][0])
            self.path = Path(_caller.filename)

        self.name = name
        self.language = language
        self.vertex = vertex
        self.fragment = fragment
        self.geometry = geometry

        self.default_input = dict()
        self.continuous_input = dict()
        self.compiled = False
        if self not in imported_shaders:
            imported_shaders[self.name] = self

        for key, value in kwargs.items():
            setattr(self, key ,value)


    def compile(self, shader_includes=True):
        if shader_includes:
            self._shader = Panda3dShader.make(self.language, do_shader_includes(self.vertex), do_shader_includes(self.fragment), do_shader_includes(self.geometry))
        else:
            self._shader = Panda3dShader.make(self.language, self.vertex, self.fragment, self.geometry)
        self.compiled = True


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
    from time import perf_counter
    t = perf_counter()
    from ursina import *
    from ursina import Ursina, Entity, held_keys, scene, EditorCamera

    app = Ursina()
    Entity(model='cube', shader=Shader())
    EditorCamera()
    print('ttttttttttttt', perf_counter() - t)
    def input(key):
        if held_keys['control'] and key == 'r':
            reload_shaders()

    def reload_shaders():
        for e in scene.entities:
            if hasattr(e, '_shader'):
                print('-------', e.shader)
                # e._shader = Panda3dShader.make(language, vertex, fragment, geometry)

    app.run()
