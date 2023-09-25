
html = '''
<html>
<head>
    <link rel="stylesheet" href="api_reference.css">
</head>
<body>
<input type="checkbox" id="checkbox" onClick="save()"></input>
<script>

function save() {
	var checkbox = document.getElementById("checkbox");
    localStorage.setItem("checkbox", checkbox.checked);
}

// loading
var checked = JSON.parse(localStorage.getItem("checkbox"));
document.getElementById("checkbox").checked = checked;

</script>
<bg></bg>
'''

groups = {
'Basics' : [
    'Ursina',
    'Entity',
    'Button',
    'Sprite',
    'Text',
    'Audio',
    ],
'Core Modules' : [
    'camera',
    'mouse',
    'window',
    'application',
    'scene',
    ],
'Graphics' : [
    'color',
    'Mesh',
    'Shader',
    'Texture',
    'Light',
    'DirectionalLight',
    'PointLight',
    'AmbientLight',
    'SpotLight',
    ],
'Procedural Models': [
    'Quad',
    'Circle',
    'Plane',
    'Grid',
    'Cone',
    'Cylinder',
    'Pipe',
    'Terrain',
    ],
'modules': [
    'input_handler',
    'mesh_importer',
    'texture_importer',
    'string_utilities',
    ],
'Animation': [
    'Animation',
    'FrameAnimation3d',
    'SpriteSheetAnimation',
    'Animator',
    'TrailRenderer',
    'curve',
    ],
'Math': [
    'ursinamath',
    'Vec2',
    'Vec3',
    'Vec4',
    'CubicBezier',
],
'Gameplay' : [
    'ursinastuff',
    'Sequence',
    'Func',
    'Keys',
],
'Collision' : [
    'raycast',
    'terraincast',
    'boxcast',
    'HitInfo',
    'Collider',
    'BoxCollider',
    'SphereCollider',
    'MeshCollider',
],
'Prefabs': [
    'Sky',
    'EditorCamera',
    'Tilemap',
    'FirstPersonController',
    'PlatformerController2d',
    'Conversation',
    'Node',
],
'UI': [
    'Button',
    'Draggable',
    'Tooltip',
    'Slider',
    'ThinSlider',
    'TextField',
    'Cursor',
    'InputField',
    'ContentTypes',
    'ButtonList',
    'ButtonGroup',
    'WindowPanel',
    'Space',
    'FileBrowser',
    'FileButton',
    'FileBrowserSave',
    'DropdownMenu',
    'DropdownMenuButton',
    'RadialMenu',
    'RadialMenuButton',
    'HealthBar',
    'ColorPicker',
],
'Editor': [
    'HotReloader',
    'GridEditor',
    'PixelEditor',
    'ASCIIEditor',
],
'Scripts': [
    'grid_layout',
    'duplicate',
    'SmoothFollow',
    'Scrollable',
    'NoclipMode',
    'NoclipMode2d',
    'build',
],
'Assets': [
    'models',
    'textures',
    'shaders',
],
}
from pathlib import Path
from pprint import pprint
import keyword
import builtins
import textwrap
from ursina import color, lerp, application



def indentation(line):
    return len(line) - len(line.lstrip())


def get_module_attributes(str):
    attrs = list()

    for l in str.split('\n'):
        if len(l) == 0:
            continue
        if l.startswith(tuple(keyword.kwlist) + tuple(dir(builtins)) + (' ', '#', '\'', '\"', '_')):
            continue
        attrs.append(l)

    return attrs


def get_classes(str):
    classes = dict()
    for c in str.split('\nclass ')[1:]:
        class_name = c.split(':', 1)[0]
        if class_name.startswith(('\'', '"')):
            continue
        # print(class_name)
        classes[class_name] = c.split(':', 1)[1]

    return classes


def get_class_scope_variables(str):
    vars = []
    for i, line in enumerate(str.split('\n')):
        if not line:
            continue
        if line.strip().startswith('_'):
            continue
        if line.strip().startswith('def'):
            break
        vars.append(line)

    return vars


def get_class_attributes(str):
    attributes = list()
    lines = str.split('\n')
    start = 0
    end = len(lines)
    for i, line in enumerate(lines):
        if line == '''if __name__ == '__main__':''':
            break

        found_init = False
        if line.strip().startswith('def __init__'):
            if found_init:
                break

            start = i
            for j in range(i+1, len(lines)):
                if (indentation(lines[j]) == indentation(line) and not lines[j].strip().startswith('def late_init')):
                    end = j
                    found_init = True
                    break


    init_section = lines[start:end]
    # print('init_section:', start, end, init_section)

    for i, line in enumerate(init_section):
        if line.strip().startswith('self.') and ' = ' in line and line.startswith(' '*8) and not line.startswith(' '*9):
            stripped_line = line.split('self.', 1)[1]
            if '.' in stripped_line.split(' ')[0] or stripped_line.startswith('_'):
                continue

            key = stripped_line.split(' = ')[0]
            value = stripped_line.split(' = ')[1]

            if i < len(init_section)-1 and indentation(init_section[i+1]) > indentation(line):
                # value = 'multiline'
                start = i
                end = i
                indent = indentation(line)
                for j in range(i+1, len(init_section)):
                    if indentation(init_section[j]) <= indent:
                        end = j
                        break

                for l in init_section[start+1:end]:
                    value += '\n' + l[4:]

            attributes.append(key + ' = ' + value)

    if '@property' in code:
        for i, line in enumerate(lines):
            if line.strip().startswith('@property'):
                name = lines[i+1].split('def ')[1].split('(')[0]

                # include comments for properties
                if '#' in lines[i+1]:
                    name += ((20-len(name)) * ' ') + '<gray>#' + lines[i+1].split('#',1)[1] + '</gray>'

                if not name in [e.split(' = ')[0] for e in attributes]:
                    attributes.append(name)

    return attributes


def get_functions(str, is_class=False):
    functions = dict()
    lines = str.split('\n')

    functions = list()
    lines = str.split('\n')
    # ignore_functions_for_property_generation = 'generate_properties(' in str

    for i, line in enumerate(lines):

        if line == '''if __name__ == '__main__':''' or 'docignore' in line:
            break
        if line.strip().startswith('def '):
            if not is_class and line.split('(')[1].startswith('self'):
                continue

            name = line.split('def ')[1].split('(')[0]
            if name.startswith('_') or lines[i-1].strip().startswith('@'):
                continue

            # if ignore_functions_for_property_generation:
            #     if name.startswith('get_') or name.startswith('set_'):
            #         continue


            params = line.replace('(self, ', '(')
            params = params.replace('(self)', '()')
            params = params.split('(', 1)[1].rsplit(')', 1)[0]

            comment = ''
            if '#' in line:
                comment = '#' + line.split('#')[1]

            functions.append((name, params, comment))

    return functions

def clear_tags(str):
    for tag in ('purple', 'olive', 'yellow', 'blue'):
        str = str.replace(f'<{tag}>', '')
        str = str.replace(f'</{tag}>', '')

    return str


def get_example(str, name=None):    # use name to highlight the relevant class
    key = '''if __name__ == '__main__':'''
    lines = list()
    example_started = False
    for l in str.split('\n'):
        if example_started:
            lines.append(l)

        if l == key:
            example_started = True

    example = '\n'.join(lines)
    example = textwrap.dedent(example)
    example = example.split('# test\n')[0]
    ignore = ('app = Ursina()', 'app.run()', 'from ursina import *')
    if 'class Ursina' in str:   # don't ignore in main.py
        ignore = ()


    lines = [e for e in example.split('\n') if not e in ignore and not e.strip().startswith('#')]

    import re
    styled_lines = list()

    for line in lines:
        line = line.replace('def ', '<purple>def</purple> ')
        line = line.replace('from ', '<purple>from</purple> ')
        line = line.replace('import ', '<purple>import</purple> ')
        line = line.replace('for ', '<purple>for</purple> ')

        line = line.replace('elif ', '<purple>elif</purple> ')
        line = line.replace('if ', '<purple>if</purple> ')
        line = line.replace(' not ', ' <purple>not</purple> ')
        line = line.replace('else:', '<purple>else</purple>:')

        line = line.replace('Entity', '<olive>Entity</olive>')
        for e in ('print', 'range', 'hasattr', 'getattr', 'setattr'):
            line = line.replace(f'{e}(' , f'<blue>{e}</blue>(')

        # colorize ursina specific params
        for e in ('enabled', 'parent', 'world_parent', 'model', 'highlight_color', 'color',
            'texture_scale', 'texture', 'visible',
            'position', 'z', 'y', 'z',
            'rotation', 'rotation_x', 'rotation_y', 'rotation_z',
            'scale', 'scale_x', 'scale_y', 'scale_z',
            'origin', 'origin_x', 'origin_y', 'origin_z',
            'text', 'on_click', 'icon', 'collider', 'shader', 'curve', 'ignore',
            'vertices', 'triangles', 'uvs', 'normals', 'colors', 'mode', 'thickness'
            ):
            line = line.replace(f'{e}=' , f'<olive>{e}</olive>=')


        # colorize numbers
        for i in range(10):
            line = line.replace(f'{i}', f'<yellow>{i}</yellow>')

        # destyle Vec2 and Vec3
        line = line.replace(f'<yellow>3</yellow>(', '3(')
        line = line.replace(f'<yellow>2</yellow>(', '2(')

        # highlight class name
        if name:
            if '(' in name:
                name = name.split('(')[0]
            line = line.replace(f'{name}(', f'<purple><b>{name}</b></purple>(')
            line = line.replace(f'={name}(', f'=<purple><b>{name}</b></purple>(')
            # line = line.replace(f'.{name}', f'.<font colorK

        if ' #' in line:
            # remove colored words inside strings
            line = clear_tags(line)
            line = line.replace(' #', ' <gray>#')
            line += '</gray>'


        styled_lines.append(line)

    lines = styled_lines
    example = '\n'.join(lines)


    # find triple qutoted strings
    if example.count("'''") % 2 == 0 and example.count("'''") > 1:
        parts = example.strip().split("'''")
        parts = [e for e in parts if e]
        is_quote = example.strip().startswith("'''")

        for i in range(not is_quote, len(parts), 2):
            parts[i] = clear_tags(parts[i])

            parts[i] = "<green>'''" + parts[i] + "'''</green>"

        example = ''.join(parts)

    # find single quoted words
    styled_lines = []
    for line in example.split('\n'):
        quotes = re.findall('\'(.*?)\'', line)
        quotes = ['\'' + q + '\'' for q in quotes]
        for q in quotes:
            line = line.replace(q, '<green>' + clear_tags(q) + '</green>')
        styled_lines.append(line)

    example = '\n'.join(styled_lines)


    return example.strip()


def is_singleton(str):
    for l in str.split('\n'):
        # if l.startswith('sys.modules['):
        if l.startswith('instance = '):
            return True

    result = False


path = application.package_folder
module_info = dict()
class_info = dict()
module_info['textures'] = ('', '', '', [], ('noise', 'grass', 'vignette', 'arrow_right', 'test_tileset', 'tilemap_test_level', 'shore', 'file_icon', 'sky_sunset', 'radial_gradient', 'circle', 'perlin_noise', 'brick', 'grass_tintable', 'circle_outlined', 'ursina_logo', 'arrow_down', 'cog', 'vertical_gradient', 'white_cube', 'horizontal_gradient', 'folder', 'rainbow', 'heightmap_1', 'sky_default',), (), ())
module_info['models'] = ('', '', '', [], ('quad', 'wireframe_cube', 'plane', 'circle', 'diamond', 'wireframe_quad', 'sphere', 'cube', 'icosphere', 'cube_uv_top', 'arrow', 'sky_dome', ), (), ())
module_info['shaders'] = ('', '', '', [], ('colored_lights_shader', 'fresnel_shader', 'projector_shader', 'instancing_shader', 'texture_blend_shader', 'matcap_shader', 'triplanar_shader', 'unlit_shader', 'geom_shader', 'normals_shader', 'transition_shader', 'noise_fog_shader', 'lit_with_shadows_shader', 'fxaa', 'camera_empty', 'ssao', 'camera_outline_shader', 'pixelation_shader', 'camera_contrast', 'camera_vertical_blur', 'camera_grayscale', ), (), ())


for f in path.glob('**/*.py'):
    with open(f, encoding='utf-8') as t:
        code = t.read()
        code = code.replace('<', '&lt').replace('>', '&gt')

        if not is_singleton(code):
            name = f.stem
            attrs, funcs = [], []
            attrs = get_module_attributes(code)
            funcs = get_functions(code)
            example = get_example(code, name)
            if attrs or funcs:
                module_info[name] = (f, '', '', [], attrs, funcs, example)

            # continue
            classes = get_classes(code)
            for class_name, class_definition in classes.items():
                print('parsing class:', class_name)

                params = ''
                if 'def __init__' in class_definition:
                    # init line
                    params =  '__init__('+ class_definition.split('def __init__(')[1].split('\n')[0][:-1]

                class_scope_vars = get_class_scope_variables(class_definition)
                attrs = get_class_attributes(class_definition)
                methods = get_functions(class_definition, is_class=True)
                example = get_example(code, class_name)

                parent_class = ''
                if ('(') in class_name:
                    parent_class = class_name.split('(')[1].split(')')[0]
                    class_name =  class_name.split('(')[0]
                class_info[class_name] = (f, parent_class, params, class_scope_vars, attrs, methods, example)
        # singletons
        else:
            module_name = f.stem
            classes = get_classes(code)
            for class_name, class_definition in classes.items():
                # print(module_name)
                attrs, methods = list(), list()
                attrs = get_class_attributes(class_definition)
                methods = get_functions(class_definition, is_class=True)
                example = get_example(code, class_name)

                module_info[module_name] = (f, '', '', [], attrs, methods, example)

def html_color(color):
    return f'hsl({color.h}, {int(color.s*100)}%, {int(color.v*100)}%)'



# make index menu
from textwrap import dedent
# html += '''<div class="parent">''' ## index container
html += '''<div class="sidebar">''' ## index container
i = 0
for group_name, group in groups.items():
    links = ''.join([f'\n            <a href="#{e}">{e}</a><br>' for e in group])
    html += f'''
    <div class="sidebar_box" style="color: hsl({30+(i*20)}deg 94% 21%);">
        <div class="group_header">{group_name}</div>
        <div class="group_content">{links}</div>
        <br>
    </div>
    '''
    i+= 1
html += '</div>\n'
html += '<main_section>\n'
html += '    <h1 class="main_header">ursina API Reference</h1>\n'
html += '    <p>v5.0.0</p>\n'
# print(module_info)
# main part
for group_name, group in groups.items():
    # links = '\n     '.join([f'<a href="#{e}">{e}</a><br>' for e in group])
    for name in group:
        init_text = ''
        is_class = name[0].isupper()
        data = None
        if name in module_info:
            data = module_info[name]
        elif name in class_info:
            data = class_info[name]

        if not data:
            continue
            print('no info found for', name)
        # f, params, attrs, methods, example = data
        location, parent_class, params, class_scope_vars, attrs, funcs, example = data
        params = params.replace('__init__', name.split('(')[0])
        params = params.replace('(self, ', '(')
        params = params.replace('(self)', '()')

        parent_class = parent_class.replace('ShowBase', '')
        parent_class = parent_class.replace('NodePath', '')
        link_to_parent_class = ''
        if parent_class:
            link_to_parent_class = f'<a style="color: gray; font-weight:normal;" href="#{parent_class}">({parent_class})</a>'

        html += (
            f'''    <div class="class_box" id="{name}">\n'''
            f'''        <h1>{name}{link_to_parent_class}</h1>\n'''
            )
        location = str(location)
        if 'ursina' in location:
            location = location.split('ursina')[-1]
            github_link = 'https://github.com/pokepetter/ursina/blob/master/ursina' + location.replace('\\', '/')
            location = location.replace('\\', '.')[:-3]
            html += f'''        <a href="{github_link}"><gray>ursina{location}</gray></a><br><br>\n'''

        if params:
            html += f'        <div class="params">{params}</div><br>\n'

        html += '        <table> <!-- attributes -->\n'

        for e in class_scope_vars:
            html += (
            f'            <tr>\n'
            f'                <td>{name}.{e.strip()}<gray></gray></td><td>{info}</td>\n'
            f'            </tr>\n'
            )


        dot = '.'
        if group_name == 'Assets':    # don't add a . for asset names
            dot = ''

        for e in attrs:
            attr_name = e
            default = ''
            info = ''

            if '# ' in e:
                attr_name, info = e.split('# ', 1)
            if ' = ' in attr_name:
                attr_name, default = attr_name.split(' = ', 1)
                default = f' = {default}'

            if info:
                info = f'<span>{info.strip()}</span>'

            html += (
                f'            <tr>\n'
                f'                <td>{dot}{attr_name}<gray>{default}</gray></td><td>{info}</td>\n'
                f'            </tr>\n'
            )

        html += '        </table><br>\n'

        if funcs:
            html += '        <div><gray>functions:</gray></div>\n'
            html += '        <table>\n'

        for e in funcs:
            html += (
                f'''            <tr>\n'''
                f'''                <td> &nbsp;{e[0]}(<gray>{e[1]}</gray>) <span>{e[2][2:]}</span></td>\n'''
                f'''            </tr>\n'''
            )

        html += '        </table><br>\n'

        if example:
            html += '    <div><gray>example:</gray></div>\n'
            html += f'    <div class="example">{example}\n</div>\n'

        # html += '\n</div></div>'
        html = html.replace('<gray></gray>', '')

        html += dedent('''
            </div>
            <br>
        ''')


html += '''
</main_section>
</body>
</html>
'''
with open('api_reference.html', 'w', encoding='utf-8') as f:
    f.write(html)
