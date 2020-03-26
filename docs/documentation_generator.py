from pathlib import Path
from pprint import pprint
import keyword
import builtins
import textwrap
from ursina import color, lerp, application

'''
samples
tutorials
'''


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
        # attributes.append('properties:\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('@property'):
                name = lines[i+1].split('def ')[1].split('(')[0]
                if not name in [e.split(' = ')[0] for e in attributes]:
                    attributes.append(name)

    return attributes


def get_functions(str, is_class=False):
    functions = dict()
    lines = str.split('\n')

    functions = list()
    lines = str.split('\n')
    for i, line in enumerate(lines):

        if line == '''if __name__ == '__main__':''' or 'docignore' in line:
            break
        if line.strip().startswith('def '):
            if not is_class and line.split('(')[1].startswith('self'):
                continue

            name = line.split('def ')[1].split('(')[0]
            if name.startswith('_') or lines[i-1].strip().startswith('@'):
                continue

            params = line.replace('(self, ', '(')
            params = params.replace('(self)', '()')
            params = params.split('(', 1)[1].rsplit(')', 1)[0]

            comment = ''
            if '#' in line:
                comment = '#' + line.split('#')[1]

            functions.append((name, params, comment))

    return functions


def get_example(str):
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
    ignore = ('app = Ursina()', 'app.run()', 'from ursina import *')
    if 'class Ursina' in str:   # don't ignore in main.py
        ignore = ()

    lines = [e for e in example.split('\n') if not e in ignore and not e.strip().startswith('#')]
    example = '\n'.join(lines)
    return example.strip()


def is_singleton(str):
    for l in str.split('\n'):
        if l.startswith('sys.modules['):
            return True

    result = False


path = application.package_folder
# print('path', path)

init_file = ''
with open(path / '__init__.py') as f:
    init_file = f.read()

# print(init_file)
most_used_info = dict()
module_info = dict()
class_info = dict()

for f in path.glob('*.py'):
    if f.name.startswith('_') or f.name == 'build.py':
        module_info['build'] = (
            'python -m ursina.build',
            {},
            '',
            '''open cmd at your project folder and run 'python -m ursina.build' to package your app for windows.'''
            )
        continue

    with open(f, encoding='utf8') as t:
        code = t.read()

        if not is_singleton(code):
            name = f.name.split('.')[0]
            attrs, funcs = list(), list()
            attrs = get_module_attributes(code)
            funcs = get_functions(code)
            example = get_example(code)
            if attrs or funcs:
                module_info[name] = ('', attrs, funcs, example)

            # continue
            classes = get_classes(code)
            for class_name, class_definition in classes.items():
                if 'Enum' in class_name:
                    class_definition = class_definition.split('def ')[0]
                    attrs = [l.strip() for l in class_definition.split('\n') if ' = ' in l]
                    class_info[class_name] = ('', attrs, '', '')
                    continue

                if 'def __init__' in class_definition:
                    # init line
                    params =  '__init__('+ class_definition.split('def __init__(')[1].split('\n')[0][:-1]
                attrs = get_class_attributes(class_definition)
                methods = get_functions(class_definition, is_class=True)
                example = get_example(code)

                class_info[class_name] = (params, attrs, methods, example)
        # singletons
        else:
            module_name = f.name.split('.')[0]
            classes = get_classes(code)
            for class_name, class_definition in classes.items():
                # print(module_name)
                attrs, methods = list(), list()
                attrs = get_class_attributes(class_definition)
                methods = get_functions(class_definition, is_class=True)
                example = get_example(code)

                module_info[module_name] = ('', attrs, methods, example)


prefab_info = dict()
for f in path.glob('prefabs/*.py'):
    if f.name.startswith('_'):
        continue

    # if f.is_file() and f.name.endswith(('.py', )):
    with open(f, encoding='utf8') as t:
        code = t.read()
        classes = get_classes(code)
        for class_name, class_definition in classes.items():
            if 'def __init__' in class_definition:
                params =  '__init__('+ class_definition.split('def __init__(')[1].split('\n')[0][:-1]
            attrs = get_class_attributes(class_definition)
            methods = get_functions(class_definition, is_class=True)
            example = get_example(code)

            prefab_info[class_name] = (params, attrs, methods, example)


script_info = dict()
for f in path.glob('scripts/*.py'):
    if f.name.startswith('_'):
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
                script_info[name] = ('', attrs, funcs, example)

        classes = get_classes(code)
        for class_name, class_definition in classes.items():
            if 'def __init__' in class_definition:
                params =  '__init__('+ class_definition.split('def __init__(')[1].split('\n')[0][:-1]
            attrs = get_class_attributes(class_definition)
            methods = get_functions(class_definition, is_class=True)
            example = get_example(code)

            script_info[class_name] = (params, attrs, methods, example)

asset_info = dict()
model_names = [f'\'{f.stem}\'' for f in path.glob('models/compressed/*.ursinamesh')]
asset_info['models'] = ('', model_names, '', '''e = Entity(model='quad')''')

texture_names = [f'\'{f.stem}\'' for f in path.glob('textures/*.*')]
asset_info['textures'] = ('', texture_names, '', '''e = Entity(model='cube', texture='brick')''')

for f in path.glob('models/procedural/*.py'):
    if f.name.startswith('_'):
        continue

    with open(f, encoding='utf8') as t:
        code = t.read()
        classes = get_classes(code)
        for class_name, class_definition in classes.items():
            if 'def __init__' in class_definition:
                params =  '__init__('+ class_definition.split('def __init__(')[1].split('\n')[0][:-1]
            attrs = get_class_attributes(class_definition)
            methods = get_functions(class_definition, is_class=True)
            example = get_example(code)

            asset_info[class_name] = (params, attrs, methods, example)


most_used_info = dict()
for name in ('Entity(NodePath)', 'Text(Entity)', 'Button(Entity)', 'mouse', 'raycaster',):
    for d in (module_info, class_info, prefab_info):
        if name in d:
            most_used_info[name] = d[name]
            del d[name]



def html_color(color):
    return f'hsl({color.h}, {int(color.s*100)}%, {int(color.v*100)}%)'

base_color = color.color(60, 1, .01)
base_color = color.color(60, 0, .99)
# background_color = color.color(0,0,.9)
background_color = lerp(base_color, base_color.invert(), .125)
background_color = lerp(base_color, base_color.invert(), 0)
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
          scrollbar-dark-shadow-color: {html_color(text_color)};
        }}

        ::-webkit-scrollbar {{ width: 8px; height: 3px;}}
        ::-webkit-scrollbar-button {{  background-color: {scrollbar_color}; }}
        ::-webkit-scrollbar-track {{  background-color: {html_color(background_color)};}}
        ::-webkit-scrollbar-track-piece {{ background-color: {html_color(background_color)};}}
        ::-webkit-scrollbar-thumb {{ height: 50px; background-color: {scrollbar_color}; border-radius: 3px;}}
        ::-webkit-scrollbar-corner {{ background-color: {html_color(background_color)};}}
        ::-webkit-resizer {{ background-color: {html_color(background_color)};}}

        a {{
          color: {link_color};
        }}

        g {{
            color: gray;
        }}

        .example {{
            # font-color: red;
            padding-left: 1em;
            background-color: {html_color(example_color)};
        }}
    </style>

    <body style="
        margin: auto;
        # background-color: hsl(0, 0%, 10%);
        # color: hsl(0, 0%, 80%);
        background-color: {html_color(background_color)};
        color: {html_color(text_color)};
        font-family: monospace;
        position: absolute;
        top:0;
        left: 24em;
        font-size: 1.25em;
        font-weight: lighter;
        max-width: 1200px;
        >
    '''
html = '<title> ursina cheat sheet</title>'
sidebar = '''<pre><div style="
    left: 0px;
    position: fixed;
    top: 0px;
    padding-top:40px;
    padding-left:20px;
    bottom: 0;
    overflow-y: scroll;
    width: 15em;
    ">'''

for i, class_dictionary in enumerate((most_used_info, module_info, class_info, prefab_info, script_info, asset_info)):
    for name, attrs_and_functions in class_dictionary.items():
        params, attrs, funcs, example = attrs_and_functions[0], attrs_and_functions[1], attrs_and_functions[2], attrs_and_functions[3]

        params = params.replace('__init__', name.split('(')[0])
        params = params.replace('(self, ', '(')
        params = params.replace('(self)', '()')

        name = name.replace('ShowBase', '')
        name = name.replace('NodePath', '')
        for parent_class in ('Entity', 'Button', 'Draggable', 'Text', 'Collider', 'Mesh', 'Prismatoid'):
            name = name.replace(f'({parent_class})', f'(<a style="color: gray;" href="#{parent_class}">{parent_class}</a>)')

        base_name = name
        if '(' in base_name:
            base_name = base_name.split('(')[0]
            base_name = base_name.split(')')[0]
        name = name.replace('(', '<g>(')
        name = name.replace(')', ')</g>')

        v = lerp(text_color.v, background_color.v, .2)
        col = color.color(50-(i*30), .9, v)
        col = html_color(col)

        sidebar += f'''<a style="color:{col};" href="#{base_name}">{base_name}</a>\n'''
        html += '\n'
        html += f'''<div id="{base_name}"><div id="{base_name}" style="color:{col}; font-size:1.75em; font-weight:normal;">{name}</div>'''
        html += '<pre style="position:relative; padding:0em 0em 2em 1em; margin:0;">'
        if params:
            params = f'<params id="params" style="color:{init_color}; font-weight:bold">{params}</params>\n'
            html += params + '\n'

        for e in attrs:
            if ' = ' in e:
                e = f'''{e.split(' = ')[0]}<g> = {e.split(' = ')[1]}</g> '''

            html += f'''{e}\n'''

        html += '\n'
        for e in funcs:
            e = f'{e[0]}(<g>{e[1]}</g>)   <g>{e[2]}</g>'
            html += e + '\n'

        if example:
            html += '\n<div class="example">' + example +'\n</div>'


        html += '\n</pre></div>'

        html = html.replace('<g></g>', '')

    sidebar += '\n'

# print(html)
sidebar += '</div>'
html += '</div>'
html = sidebar + style + html + '</body>'
with open('cheat_sheet.html', 'w', encoding='utf-8') as f:
    f.write(html)
