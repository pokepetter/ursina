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


    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        from ursina.scene import instance as scene
        if hasattr(self, 'default_input') and key in self.default_input:
            print('setting global shader input:', key, value)
            for entity_with_this_shader in [e for e in scene.entities if e.shader == self]:
                entity_with_this_shader.set_shader_input(key, value)


    def __add__(self, other):
        self_vertex_lines = self.vertex.split('\n')
        vertex_version = ''
        def get_version(shader_code):
            return shader_code.split('#version', 1)[1].split('\n')[0]

        this_version, other_version = get_version(self.vertex), get_version(other.vertex)
        if this_version != other_version:
            raise Exception(f'Vertex shaders does not have matching versions: {this_version}, {other_version}')
        # if get_version(self.fragment) != get_version(other.fragment):
        #     raise Exception('Vertex shaders does not have mathcing versions.')

        # inputs = set()
        vertex_shader_input_self = [l for l in self.vertex.split('\n') if l.startswith('in ')]
        vertex_shader_input_other = [l for l in other.vertex.split('\n') if l.startswith('in ')]
        vertex_shader_uniforms_self = [l for l in self.vertex.split('\n') if l.startswith('uniform ')]
        vertex_shader_uniforms_other = [l for l in other.vertex.split('\n') if l.startswith('uniform ')]
        vertex_shader_output_self = [l for l in self.vertex.split('\n') if l.startswith('out ')]
        vertex_shader_output_other = [l for l in other.vertex.split('\n') if l.startswith('out ')]

        import re
        def extract_functions(glsl):
            header_pattern = re.compile(r'([a-zA-Z_]\w*)\s+([a-zA-Z_]\w*)\s*\((.*?)\)\s*\{', re.DOTALL)
            functions = {}

            for match in header_pattern.finditer(glsl):
                start = match.start()

                brace_pos = glsl.find('{', match.end() - 1)
                depth = 1
                i = brace_pos + 1

                while i < len(glsl) and depth:
                    if glsl[i] == '{':
                        depth += 1
                    elif glsl[i] == '}':
                        depth -= 1
                    i += 1

                functions[f'{match.group(2)}->{match.group(1)}'] = {
                    "return_type": match.group(1),
                    "name": match.group(2),
                    "args": match.group(3).strip(),
                    "source": glsl[start:i],
                    "returns": [l for l in glsl[start:i].split('\n') if l.lstrip().startswith('return ')],
                }

            return functions

        vertex_shader_functions = extract_functions(self.vertex)
        for name, func_data in extract_functions(other.vertex).items():
            if name not in vertex_shader_functions:
                vertex_shader_functions[name] = func_data
                continue

            # if both shader have identical function name and return type

            # if name == 'main':
            #     original_function = vertex_shader_functions[name]
            #     if len(original_function['returns'])

        # print(vertex_shader_functions_self)

        # vertex_functions_self = [l for l in self.vertex.split('\n') if l.startswith('uniform ') or l.startswith('in ') or l.startswith('out ')]
        # vertex_functions_other = [l for l in self.vertex.split('\n') if l.startswith('uniform ') or l.startswith('in ') or l.startswith('out ')]
        # combined_shader_input = set(vertex_shader_input_self, vertex_shader_input_other)

        combined_vertex_shader_input = set(vertex_shader_input_self + vertex_shader_input_other)
        combined_vertex_shader_uniforms = set(vertex_shader_uniforms_self + vertex_shader_uniforms_other)
        combined_vertex_shader_output = set(vertex_shader_output_self + vertex_shader_output_other)

        from textwrap import dedent
        combined_shader = dedent(f'''\
#version {this_version}
// vertex in
{'\n'.join(combined_vertex_shader_input)}
// vertex uniform
{'\n'.join(combined_vertex_shader_uniforms)}
// vertex out
{'\n'.join(combined_vertex_shader_output)}
''')
        print(combined_shader)
        # if self.vertex.split('#version ',1)[] == #version


        # if 'void main()' in self.fragment and 'void main()' in other.fragment:
        #     # merge fragment mains






if __name__ == '__main__':
    from time import perf_counter
    t = perf_counter()
    from ursina import *
    from ursina import Ursina, Entity, held_keys, scene, EditorCamera

    app = Ursina()
    Entity(model='cube', shader=Shader(name='test_shader'))
    EditorCamera()
    def input(key):
        if held_keys['control'] and key == 'r':
            reload_shaders()

    def reload_shaders():
        for e in scene.entities:
            if hasattr(e, '_shader'):
                print('-------', e.shader)
                # e._shader = Panda3dShader.make(language, vertex, fragment, geometry)


    from ursina.shaders.unlit_shader import unlit_shader
    from ursina.shaders.matcap_shader import matcap_shader

    combined_shader = unlit_shader + matcap_shader
    print(combined_shader)

    app.run()
