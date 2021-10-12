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
                if (indentation(lines[j]) == indentation(line)
                and not lines[j].strip().startswith('def late_init')
                ):
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

            if i < len(init_section) and indentation(init_section[i+1]) > indentation(line):
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
    ignore_functions_for_property_generation = 'generate_properties(' in str

    for i, line in enumerate(lines):

        if line == '''if __name__ == '__main__':''' or 'docignore' in line:
            break
        if line.strip().startswith('def '):
            if not is_class and line.split('(')[1].startswith('self'):
                continue

            name = line.split('def ')[1].split('(')[0]
            if name.startswith('_') or lines[i-1].strip().startswith('@'):
                continue

            if ignore_functions_for_property_generation:
                if name.startswith('get_') or name.startswith('set_'):
                    continue


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
most_used_info = dict()
module_info = dict()
class_info = dict()

# ignore files that are not committed
ignored_files = list()
for f in ignored_files:
    print('ignoring:', f)
ignored_files.append(path / 'gamepad.py')

for f in path.glob('*.py'):
    if f in ignored_files:
        continue
    if f.name.startswith('_') or f.name == 'build.py':
        module_info['build'] = (
            f,
            'python -m ursina.build',
            {},
            '',
            '''open cmd at your project folder and run 'python -m ursina.build' to package your app for windows.'''
            )
        continue

    with open(f, encoding='utf8') as t:
        code = t.read()
        code = code.replace('<', '&lt').replace('>', '&gt')

        if not is_singleton(code):
            name = f.stem
            attrs, funcs = list(), list()
            attrs = get_module_attributes(code)
            funcs = get_functions(code)
            example = get_example(code, name)
            if attrs or funcs:
                module_info[name] = (f, '', attrs, funcs, example)

            # continue
            classes = get_classes(code)
            for class_name, class_definition in classes.items():
                if 'Enum' in class_name:
                    class_definition = class_definition.split('def ')[0]
                    attrs = [l.strip() for l in class_definition.split('\n') if ' = ' in l]
                    class_info[class_name] = (f, '', attrs, '', '')
                    continue

                if 'def __init__' in class_definition:
                    # init line
                    params =  '__init__('+ class_definition.split('def __init__(')[1].split('\n')[0][:-1]
                attrs = get_class_attributes(class_definition)
                methods = get_functions(class_definition, is_class=True)
                example = get_example(code, class_name)

                class_info[class_name] = (f, params, attrs, methods, example)
        # singletons
        else:
            module_name = f.name.split('.')[0]
            classes = get_classes(code)
            for class_name, class_definition in classes.items():
                # print(module_name)
                attrs, methods = list(), list()
                attrs = get_class_attributes(class_definition)
                methods = get_functions(class_definition, is_class=True)
                example = get_example(code, class_name)

                module_info[module_name] = (f, '', attrs, methods, example)


prefab_info = dict()
for f in path.glob('prefabs/*.py'):
    if f.name.startswith('_') or f in ignored_files:
        continue

    with open(f, encoding='utf8') as t:
        code = t.read()
        code = code.replace('<', '&lt').replace('>', '&gt')

        classes = get_classes(code)
        for class_name, class_definition in classes.items():
            if 'def __init__' in class_definition:
                params =  '__init__('+ class_definition.split('def __init__(')[1].split('\n')[0][:-1]
            attrs = get_class_attributes(class_definition)
            methods = get_functions(class_definition, is_class=True)
            example = get_example(code, class_name)

            prefab_info[class_name] = (f, params, attrs, methods, example)


script_info = dict()
for f in path.glob('scripts/*.py'):
    if f.name.startswith('_') or f in ignored_files:
        continue

    # if f.is_file() and f.name.endswith(('.py', )):
    with open(f, encoding='utf8') as t:

        code = t.read()
        if not 'class ' in code:
            name = f.name.split('.')[0]
            attrs, funcs = list(), list()
            attrs = get_module_attributes(code)
            funcs = get_functions(code)
            example = get_example(code)
            if attrs or funcs:
                script_info[name] = (f, '', attrs, funcs, example)

        classes = get_classes(code)
        for class_name, class_definition in classes.items():
            if 'def __init__' in class_definition:
                params =  '__init__('+ class_definition.split('def __init__(')[1].split('\n')[0][:-1]
            attrs = get_class_attributes(class_definition)
            methods = get_functions(class_definition, is_class=True)
            example = get_example(code, class_name)

            script_info[class_name] = (f, params, attrs, methods, example)

asset_info = dict()
model_names = [f'\'{f.stem}\'' for f in path.glob('models_compressed/*.ursinamesh')]
asset_info['models'] = ('', '', model_names, '', '''e = Entity(model='quad')''')

texture_names = [f'\'{f.stem}\'' for f in path.glob('textures/*.*')]
asset_info['textures'] = ('', '', texture_names, '', '''e = Entity(model='cube', texture='brick')''')

shaders = [f'{f.stem}' for f in path.glob('shaders/*.*')] + [f'{f.stem}' for f in path.glob('shaders/screenspace_shaders/*.*')]
shaders = [e for e in shaders if not e.startswith('_')]
asset_info['shaders'] = ('', '', shaders, '', '''from ursina.shaders import normals_shader\ne = Entity(shader=normals_shader)''')

for f in path.glob('models/procedural/*.py'):
    if f.name.startswith('_') or f in ignored_files:
        continue

    with open(f, encoding='utf8') as t:
        code = t.read()
        classes = get_classes(code)
        for class_name, class_definition in classes.items():
            if 'def __init__' in class_definition:
                params =  '__init__('+ class_definition.split('def __init__(')[1].split('\n')[0][:-1]
            attrs = get_class_attributes(class_definition)
            methods = get_functions(class_definition, is_class=True)
            example = get_example(code, class_name)

            asset_info[class_name] = (f, params, attrs, methods, example)


most_used_info = dict()
for name in ('Entity(NodePath)', 'Text(Entity)', 'Button(Entity)', 'mouse', 'raycaster',):
    for d in (module_info, class_info, prefab_info):
        if name in d:
            most_used_info[name] = d[name]
            del d[name]



def html_color(color):
    return f'hsl({color.h}, {int(color.s*100)}%, {int(color.v*100)}%)'


def make_html(style, file_name):
    if style == 'light':
        base_color = color.color(60, 0, .99)
        background_color = lerp(base_color, base_color.invert(), 0)
    else:
        base_color = color.color(60, 1, .01)
        background_color = lerp(base_color, base_color.invert(), .125)

    text_color = lerp(background_color, background_color.invert(), .9)
    example_color = lerp(background_color, text_color, .1)
    scrollbar_color = html_color(lerp(background_color, text_color, .1))
    link_color = html_color(color.gray)
    init_color = html_color(base_color.invert())

    style = f'''
        <style>
            html {{
              scrollbar-face-color: {html_color(text_color)};
              scrollbar-base-color: {html_color(text_color)};
              scrollbar-3dlight-color: {html_color(text_color)}4;
              scrollbar-highlight-color: {html_color(text_color)};
              scrollbar-track-color: {html_color(background_color)};
              scrollbar-arrow-color: {html_color(background_color)};
              scrollbar-shadow-color: {html_color(text_color)};
              scrollbar-darkshadow-color: {html_color(text_color)};
            }}

            ::-webkit-scrollbar {{ width: 8px; height: 3px;}}
            ::-webkit-scrollbar {{ width: 8px; height: 3px;}}
            ::-webkit-scrollbar-button {{  background-color: {scrollbar_color}; }}
            ::-webkit-scrollbar-track {{  background-color: {html_color(background_color)};}}
            ::-webkit-scrollbar-track-piece {{ background-color: {html_color(background_color)};}}
            ::-webkit-scrollbar-thumb {{ height: 50px; background-color: {scrollbar_color}; border-radius: 3px;}}
            ::-webkit-scrollbar-corner {{ background-color: {html_color(background_color)};}}
            ::-webkit-resizer {{ background-color: {html_color(background_color)};}}

            body {{
                margin: auto;
                background-color: {html_color(background_color)};
                color: {html_color(text_color)};
                font-family: monospace;
                position: absolute;
                top:0;
                left: 24em;
                font-size: 1.375em;
                font-weight: lighter;
                max-width: 100%;
                overflow-x: hidden;
                white-space: pre-wrap;
            }}
            a {{
              color: {link_color};
            }}

            purple {{color: hsl(289.0, 50%, 50%);}}
            gray {{color: gray;}}
            olive {{color: olive;}}
            yellow {{color: darkgoldenrod;}}
            green {{color: seagreen;}}
            blue {{color: hsl(210, 50%, 50%);}}

            .example {{
                padding-left: 1em;
                background-color: {html_color(example_color)};
            }}
            .params {{
                color:{init_color};
                font-weight:bold;
            }}
        </style>
        '''
    # return style


    html = '<title> ursina cheat sheet</title>'
    html += '''
        <b>Ursina cheat sheet</b>

        This document lists most modules and classes in ursina. Each section is structured as follows:

        ClassName(BaseClass)
            module location

            parameters
                How instantiate the class, ie. Button(text='', **kwargs).
                '**kwargs' in this case, means you can give it optional keyword arguments.
                For example, Button('Start', scale=.25, color=color.blue, position=(-.1,.25)) also includes
                information on how big the button should be, its color and its position.

            attributes
                Names of values we can get/set, sometimes followed by its starting value and a short explanation.
                For example, 'scale', 'color' and 'position' are
                attributes we gave the Button above. These are members of Entity, which Button class
                inherits from, so the Button class can also access these.

            methods/functions
                these ends with (), which means they are functions that can be called.
                Also lists their parameters and default arguments.
                For example, Entity has a method called 'look_at()'. You need to give it a
                'target' (an Entity or position) to look at and optionally say
                which axis will be facing the target.

            example

        You can search the document with Ctrl+F for instant search results.
    '''

    sidebar = '''
<div class="sidebar" style="
left: 0px;
position: fixed;
top: 0px;
padding-top:40px;
padding-left:20px;
bottom: 0;
overflow-y: scroll;
width: 15em;
z-index: 1;
">
<a href="cheat_sheet.html">light</a>  <a href="cheat_sheet_dark.html">dark</a>

'''

    for i, class_dictionary in enumerate((most_used_info, module_info, class_info, prefab_info, script_info, asset_info)):
        for name, attrs_and_functions in class_dictionary.items():
            print('generating docs for', name)
            location, params, attrs, funcs, example = attrs_and_functions

            params = params.replace('__init__', name.split('(')[0])
            params = params.replace('(self, ', '(')
            params = params.replace('(self)', '()')

            name = name.replace('ShowBase', '')
            name = name.replace('NodePath', '')
            for parent_class in ('Entity', 'Button', 'Draggable', 'Text', 'Collider', 'Mesh', 'Pipe'):
                name = name.replace(f'({parent_class})', f'(<a style="color: gray;" href="#{parent_class}">{parent_class}</a>)')

            base_name = name
            if '(' in base_name:
                base_name = base_name.split('(')[0]
                base_name = base_name.split(')')[0]
            name = name.replace('(', '<gray>(')
            name = name.replace(')', ')</gray>')

            v = lerp(text_color.v, background_color.v, .2)
            # v = .5
            col = color.color(50-(i*30), .9, v)
            col = html_color(col)

            sidebar += f'''<a style="color:{col};" href="#{base_name}">{base_name}</a>\n'''
            html += '\n'
            html += f'''<div id="{base_name}"><div id="{base_name}" style="color:{col}; font-size:1.75em; font-weight:normal;">{name}</div>'''
            html += '<div style="position:relative; padding:0em 0em 2em 1em; margin:0;">'
            # location
            location = str(location)
            if 'ursina' in location:
                location = location.split('ursina')[-1]
                github_link = 'https://github.com/pokepetter/ursina/blob/master/ursina' + location.replace('\\', '/')
                location = location.replace('\\', '.')[:-3]
                html += f'''<a href="{github_link}"><gray>ursina{location}</gray></a><br><br>'''

            if params:
                params = f'<params class="params">{params}</params>\n'
                html += params + '\n'

            for e in attrs:
                if ' = ' in e:
                    e = f'''{e.split(' = ')[0]}<gray> = {e.split(' = ')[1]}</gray> '''

                html += f'''{e}\n'''

            html += '\n'
            for e in funcs:
                e = f'{e[0]}(<gray>{e[1]}</gray>)   <gray>{e[2]}</gray>'
                html += e + '\n'

            if example:
                html += '\n<div class="example">' + example +'\n</div>'


            html += '\n</div></div>'

            html = html.replace('<gray></gray>', '')

        sidebar += '\n'

    sidebar += '</div>'
    html += '</div>'

    html = sidebar + style + '<div id="content">' + html + '</div>' + '</body>'
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(html)

make_html('light', 'cheat_sheet.html')
make_html('dark', 'cheat_sheet_dark.html')
