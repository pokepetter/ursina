import ast
from typing import Any, Dict, List
from pathlib import Path
import tomllib
from ursina.string_utilities import camel_to_snake
import sswg
import tokenize
from io import StringIO
import textwrap



class ClassInfo:
    def __init__(self):
        self.name = None
        self.module = None
        self.base_classes = []
        self.class_variables = []
        self.init_args = []
        self.instance_variables = []
        self.methods = []
        self.properties = []
        self.examples = []
        self.line_number = None

class ModuleInfo:
    def __init__(self):
        self.name = ''
        self.path = ''
        self.imports = []
        self.variables = []
        self.functions = []
        self.classes = []
        self.tests = []
        self.examples = []
        self.is_singleton = False   # this is ursina specific. if a module uses a class (same name as module, but pascal cased), and a 'instance' variable, we should render the class info instead of the module info. for example, window, camera and mouse use this technique to have properties even though they look like modules to the user.

class VarInfo:
    def __init__(self, name='', type_hint=None, default_value=..., comment='', line_number:int=None):
        self.name = name
        self.type_hint = type_hint
        self.default_value = default_value
        self.examples = []
        self.comment = comment
        self.line_number = line_number


class FunctionInfo:
    def __init__(self, name='', type_hint=None, input_args:[VarInfo]=..., comment='', decorators=None, module=None, from_class=None, line_number:int=None):
        self.module = module
        self.from_class = from_class
        self.name = name
        self.type_hint = type_hint
        self.input_args = input_args
        self.comment = comment
        self.decorators = decorators or []
        self.examples = []
        self.line_number = line_number

class Example:
    def __init__(self, name='', content=''):
        self.name = name
        self.content = content


def extract_var_info(node):
    # Regular assignment
    if isinstance(node, ast.Assign):
        for target in node.targets:
            # Module/class level: x = ...
            if isinstance(target, ast.Name):
                return VarInfo(
                    name=target.id,
                    default_value=ast.unparse(node.value) if node.value else None,
                    line_number=target.lineno,
                )
            # # else:
            # #     print(isinstance(target, ast.Attribute), isinstance(target.value, ast.Name), target.value.id)
            # # Instance variable: self.x = ...
            # if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
            #     return VarInfo(
            #         name=target.value.id + target.attr,
            #         default_value=ast.unparse(node.value) if node.value else None
            #     )

    # Annotated assignment (with type hint)
    elif isinstance(node, ast.AnnAssign):
        target = node.target
        # Module/class level: x: int = ...
        if isinstance(target, ast.Name):
            return VarInfo(
                name=target.id,
                type_hint=ast.unparse(node.annotation) if node.annotation else None,
                default_value=ast.unparse(node.value) if node.value else None,
                line_number=target.lineno,
            )

        # else:
        #     print(isinstance(target, ast.Attribute), isinstance(target.value, ast.Name), target.value.id)
        # Instance variable: self.x: int = ...
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
            print('self.', target.attr)
            return VarInfo(
                name=target.attr,
                type_hint=ast.unparse(node.annotation) if node.annotation else None,
                default_value=ast.unparse(node.value) if node.value else None,
                line_number=target.lineno,
            )

    return None


def extract_function_args(func_node):
    args = func_node.args.args
    defaults = func_node.args.defaults

    num_args = len(args)
    num_defaults = len(defaults)
    default_offset = num_args - num_defaults

    result = []

    for i, arg in enumerate(args):
        var_info = VarInfo()
        var_info.name = arg.arg
        var_info.type_hint = ast.unparse(arg.annotation) if arg.annotation else None

        # Match defaults from the right
        if i >= default_offset:
            default_expr = defaults[i - default_offset]
            var_info.default_value = ast.unparse(default_expr)
        else:
            var_info.default_value = None

        result.append(var_info)

    return result




def extract_inline_comments(source_code):
    comments = {}
    tokens = tokenize.generate_tokens(StringIO(source_code).readline)
    for tok_type, tok_string, (lineno, _), _, _ in tokens:
        if tok_type == tokenize.COMMENT:
            comments[lineno] = tok_string.lstrip('#').strip()
    return comments

def extract_example(str, name=None):    # use name to highlight the relevant class
    key = '''if __name__ == '__main__':'''
    lines = []
    example_started = False
    for l in str.split('\n'):
        if example_started:
            lines.append(l)

        if l == key:
            example_started = True

    example = '\n'.join(lines)
    example = textwrap.dedent(example)
    # example = example.split('# test\n')[0]
    # ignore = ('app = Ursina()', 'app.run()', 'from ursina import *')
    ignore = ()
    # if 'class Ursina' in str:   # don't ignore in main.py
    #     ignore = ()

    lines = [e for e in example.split('\n') if not e in ignore and not e.strip().startswith('#')]
    text = '\n'.join(lines)
    return text


def is_singleton(source_code, module_name):
    for l in source_code.split('\n'):
        if l.startswith(f'instance = {snake_to_camel(module_name).title()}('):
            return True
    return False

def get_package_version(package_path:Path):
    with (package_path / 'pyproject.toml').open('rb') as f:
        data = tomllib.load(f)

    version = data['project']['version']
    return version


def analyze_module(source_code: str, path:Path=None) -> ModuleInfo:
    tree = ast.parse(source_code)
    inline_comments = extract_inline_comments(source_code)

    module_info = ModuleInfo()
    module_info.path = path
    module_info.examples.append(Example(name='', content=extract_example(source_code)))
    module_info.is_singleton = is_singleton(source_code, path.stem)

    for node in tree.body:
         # module level variables
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            var_info = extract_var_info(node)
            if var_info:
                module_info.variables.append(var_info)

        # module level functions
        elif isinstance(node, ast.FunctionDef):
            module_info.functions.append(FunctionInfo(
                name = node.name,
                module = module_info,
                type_hint = ast.unparse(node.returns) if node.returns else None,
                input_args = extract_function_args(node),
                decorators = [ast.unparse(d) for d in node.decorator_list],
                comment = inline_comments.get(node.lineno),
                line_number=node.lineno,
                )
            )

        # classes
        if isinstance(node, ast.ClassDef):
            class_info = ClassInfo()
            module_info.classes.append(class_info)
            class_info.name = node.name
            class_info.base_classes = [ast.unparse(base) for base in node.bases] if node.bases else []


            for statement in node.body:
                # class level variables
                if isinstance(statement, ast.Assign):
                    for target in statement.targets:
                        if isinstance(target, ast.Name):
                            name = target.id
                            default_value = ast.unparse(statement.value) if statement.value else None
                            class_info.class_variables.append(VarInfo(
                                name=name,
                                default_value=default_value,
                                comment=inline_comments.get(target.lineno),
                                line_number=target.lineno,
                                ))

                # class level variables with type hint
                elif isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
                    class_info.class_variables.append(extract_var_info(statement))

                # methods
                elif isinstance(statement, ast.FunctionDef):
                    method_name = statement.name
                    class_info.methods.append(FunctionInfo(
                        module = module_info,
                        from_class = class_info,
                        name = statement.name,
                        # type_hint = ast.unparse(node.returns) if node.returns else None,
                        input_args = [e for e in extract_function_args(statement) if e.name != 'self'],
                        decorators = [ast.unparse(d) for d in statement.decorator_list],
                        comment = inline_comments.get(statement.lineno),
                        line_number = statement.lineno,
                        )
                    )

                    if method_name == '__init__':
                        # Find instance variables: self.xxx = ...
                        for init_statement in ast.walk(statement):
                            if isinstance(init_statement, ast.Assign):
                                for target in init_statement.targets:
                                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                        class_info.instance_variables.append(VarInfo(
                                            name=target.attr,
                                            default_value=ast.unparse(init_statement.value) if init_statement.value else None,
                                            comment=inline_comments.get(target.lineno),
                                            line_number=statement.lineno,
                                        ))
    return module_info


if __name__ == '__main__':
    from ursina import application
    # with open(application.package_folder / 'application.py', 'r') as f:
    # with open(application.package_folder / 'entity.py', 'r') as f:
    #     module_info = analyze_module(f.read())
    #     print('module name:', module_info.name)
    #     print('--- module variables ---')
    #     for e in module_info.variables:
    #         # print('module level var:', e)
    #         assert type(e) == VarInfo
    #         if e.name.startswith('_'):
    #             continue
    #         type_hint = f': {e.type_hint}' if e.type_hint is not None else ''
    #         print(f'    {e.name} {type_hint}= {e.default_value}')

    #     print('--- module functions ---')
    #     for function_info in module_info.functions:
    #         print(function_info)

    #     for class_info in module_info.classes:
    #         print('--- class ---')
    #         print(f'class: {class_info.name}({', '.join(class_info.base_classes)})')
    #         print('--- class_variables ---')
    #         for e in class_info.class_variables:
    #             assert type(e) == VarInfo
    #             if e.name.startswith('_'):
    #                 continue
    #             # print(f'    {class_info.name}.{e.name} = ')
    #             type_hint = f': {e.type_hint}' if e.type_hint is not None else ''
    #             print(f'    {e.name} {type_hint}= {e.default_value}')

    #         print('--- init ---')
    #         print(f'{class_info.name}(')
    #         for e in class_info.init_args:
    #             assert type(e) == VarInfo
    #             if e.name.startswith('_'):
    #                 continue
    #             type_hint = f': {e.type_hint}' if e.type_hint is not None else ''
    #             print(f'    {e.name} {type_hint}= {e.default_value}')
    #         print('    )')

    #         print('--- properties ---')
    #         for e in class_info.properties:
    #             print('   ', e)
    #         # print('args:', class_info.init_args)



if __name__ == '__main__':
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
            'array_tools',
            'Array2D',
            'Array3D',
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
            # 'Node',
        ],
        'UI': [
            'Button',
            'Draggable',
            'Tooltip',
            'Slider',
            'ThinSlider',
            'TextField',
            # 'Cursor',
            'InputField',
            'ContentTypes',
            'Checkbox',
            'ButtonList',
            'ButtonGroup',
            'WindowPanel',
            # 'Space',
            'FileBrowser',
            # 'FileButton',
            'FileBrowserSave',
            'DropdownMenu',
            # 'DropdownMenuButton',
            'RadialMenu',
            # 'RadialMenuButton',
            'HealthBar',
        ],
        'Editor': [
            'HotReloader',
            'GridEditor',
            'PixelEditor',
            'ASCIIEditor',
            'ColorPicker',
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
        ],
        'Shaders': [
            'unlit_shader',
            'lit_with_shadows_shader',
            'matcap_shader',
            'colored_lights_shader',
            'fresnel_shader',
            'projector_shader',
            'texture_blend_shader',
            'instancing_shader',
            'triplanar_shader',
            'normals_shader',
            'transition_shader',
            'fxaa',
            'ssao',
            'camera_outline_shader',
            'pixelation_shader',
            'camera_contrast',
            'camera_vertical_blur',
            'camera_grayscale',
        ],
        }

    from ursina import *
    import sys

    import pkgutil
    import importlib
    from pprint import pprint

    def get_all_modules_in_package(package):
        modules = []
        for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            try:
                # print('Importing:', modname)
                module = importlib.import_module(modname)
                modules.append(module)
            except Exception as e:
                print_warning(f"Failed to import {modname}: {e}")
        return modules

    import ursina

    all_modules = get_all_modules_in_package(ursina)
    modules = [ursina, ] + get_all_modules_in_package(ursina)

    module_infos = dict()
    for mod in modules:
        with open(mod.__file__, 'r') as f:
            source_code = f.read()

        # print(mod.__file__)
        module_base_name = mod.__name__
        if '.' in module_base_name:
            module_base_name = module_base_name.split('.')[-1]

        relative_path = Path(mod.__file__.split('ursina')[-1])

        modinf = analyze_module(source_code, relative_path)
        for cls in modinf.classes:
            cls.module = modinf
        module_infos[module_base_name] = modinf
        module_infos[module_base_name].name = module_base_name
        module_infos[module_base_name].path = Path(mod.__file__)


    # for e in module_infos:
    #     print('---', e)
    # package_info = {mod.__name__ : analyze_module(mod) for mod in modules}
    # module_infos = {key : value for key, value in package_info.items() if not key.startswith('_')}
    class_infos = dict()

    for module_name, modinf in module_infos.items():
        for clsinf in modinf.classes:
            if clsinf.name.startswith('_'):
                continue
            class_infos[clsinf.name] = clsinf
            # print(clsinf.name)

    def render_url_section(path: Path):
        package_folder = application.package_folder.parent
        if package_folder.name not in path.parts:
            return None

        relative_path = path.relative_to(package_folder)
        github_link = f'https://github.com/pokepetter/{package_folder.name}/tree/{version_tag}/{relative_path.as_posix()}'
        dotted_path = '.'.join(relative_path.with_suffix('').parts)
        return f'<gray>&lt;/&gt;</gray><a href="{github_link}"> {dotted_path}</a>\n'


    def add_links(function_info):
        text = '<div class="links">'

        package_folder = application.package_folder.parent
        path = None
        if function_info.module:
            path = function_info.module.path

        if path is None:
            print_warning('missing url for:', function_info.name)
        else:
            if package_folder.name not in path.parts:
                return None

            relative_path = path.relative_to(package_folder)
            github_link = f'https://github.com/pokepetter/{package_folder.name}/tree/{version_tag}/{relative_path.as_posix()}#L{function_info.line_number}'
            text += f'  <a href="{github_link}" alt="Source Code" title="View Source Code" style="font-size:.75em;">&lt;/&gt;</a>'


        permalink = f'#{function_info.name}'
        text += f'  <a href="{permalink}" onclick="navigator.clipboard.writeText(\'{permalink}\')" title="Copy permalink">◃-</a>'
        text += '</div>'
        return text


    def render_function_info(function_info):
        text = f'{function_info.name}('
        for i, var in enumerate(function_info.input_args):
            if i > 0:
                text += ', '
            if len(function_info.input_args) > 8:
                text += '\n    '

            type_hint = f': {var.type_hint}' if var.type_hint is not None else ''
            if var.default_value != ...:
                default_value = var.default_value if len(str(var.default_value)) < 32 else f'{var.default_value[:29]}...'

            text += f'{var.name}{type_hint}={default_value}'

        if len(function_info.input_args) > 8:
            text += '\n    '
        text += ')'

        return text


    def render_function_section(function_info):
        # if method_info.decorators:
        #     print('decorators:', method_info.name, method_info.decorators)
        function_usage = render_function_info(function_info)

        text = dedent(f'''\
            # {function_info.name}()
            ''')

        if function_usage != f'{function_info.name}()':
            text += f'```\n{function_usage}\n```\n'

        if function_info.comment:
            text += f'<purple>{function_info.comment}</purple>\n'


        # examples_folder = application.package_folder.parent / 'examples'
        example_file_base_name = function_info.name
        if function_info.from_class:
            example_file_base_name = f'{function_info.from_class.name}_{example_file_base_name}'

        for separate_example_file in Path('.').glob(f'{example_file_base_name}_example*.py'):
            print('found external example:', separate_example_file)
            example_name = separate_example_file.stem.split('example')[1]
            if not example_name:
                example_name = 'Example'
            text += f'{example_name}\n'

            with separate_example_file.open('r') as f:
                text += dedent(f'''\
```
{f.read()}
```
''')
        text += add_links(function_info) +'\n'
        text += '<hr></hr>'
        return text


    def render_variable_info(var:VarInfo, prefix='.', truncate_at:int=None, add_comment=False):
        type_hint = f': {var.type_hint}' if var.type_hint is not None else ''
        default_value = var.default_value
        if truncate_at is not None and len(str(var.default_value)) > truncate_at:
            default_value = f'{var.default_value[:20]}...'

        return f'{prefix}{var.name} {type_hint}<gray>= {default_value}</gray>'


    def render_variable_section(var):
        text = ''
        text += dedent(f'''\
            # .{var.name}
            ''')

        if var.type_hint is not None:
            text += dedent(f'''\
                'type: `{var.type_hint}`'
                ''')

        text += dedent(f'''\
            <gray>default: </gray>`{var.default_value if len(var.default_value) <= 50 else var.default_value[:50]+'...'}`
            ''')
        if var.comment:
            text += f'<purple>{var.comment}</purple>\n'

        text += dedent('''\
            <hr></hr>
        ''')
        return text


    def render_property_section(method_info):
                text = ''
                text += dedent(f'''\
                    # {method_info.base_name}
                    ''')
                if method_info.comment:
                    text += dedent(f'''\
                        <purple>{method_info.comment}</purple>
                        ''')
                text += add_links(method_info)
                text += dedent('''\
                    <hr></hr>
                    ''')
                return text


    singleton_infos = {key : value for key, value in module_infos.items() if value.is_singleton}
    module_infos = {key : value for key, value in module_infos.items() if not value.is_singleton}

    pages = flatten_list(groups.values())

    # get version tag
    package_version = get_package_version(application.package_folder.parent)
    version_tag = 'v' + package_version.replace('.','_')
    print('package version:', package_version, 'version_tag:', version_tag)
    output_folder = Path(f'api_reference_{version_tag}/')
    output_folder.mkdir(parents=True, exist_ok=True)

    # add front page
    front_page_content = dedent(f'''\
        #center
        ### ursina API Reference
        `{package_version}`
        #left

        ''')

    front_page_content += dedent('''\
        <div class="grid-container">''')

    for group_name, group in groups.items():
        front_page_content += '<div class="group-box">'
        front_page_content += f'<b>{group_name}</b>\n'
        for page_name in group:
            front_page_content += f'<a href="{camel_to_snake(page_name)}.html">{page_name}</a>\n'
        front_page_content += '</div>'

    front_page_content += '</div>'

    html_content = sswg.sswg_to_html(front_page_content, title='ursina API reference')
    html_content = '''
        <style>
        .grid-container {display: grid; grid-template-columns: repeat(auto-fill, minmax(19%, 1fr)); gap: 1%;}
        .group-box {padding: 10px; padding-top: 2em;}
        //.group-box h3 {margin-top:0;}
        </style>''' + html_content
    html_content = html_content.replace('href="sswg.css">', 'href="../sswg.css">')
    html_content = html_content.replace('href="style.css">', 'href="../style.css">')
    with open(output_folder / 'index.html', 'w') as f:
        f.write(html_content)


    # make .sswgs documents for each page
    for name in pages:
        # links = '\n     '.join([f'<a href="#{e}">{e}</a><br>' for e in group])
        # print('look for:', name, name in module_infos)
        if name not in module_infos and name not in class_infos and name not in singleton_infos:
            print_warning('missing module/class info for:', name)
            continue

        text = ''
        text += f'### {name}\n'

        ### modules ###
        if name in module_infos:
            module_info = module_infos[name]
            text += render_url_section(module_info.path)

            if Path(f'images/{name}.webp').exists():
                text += f'#image ../images/{name}.webp\n'

            if module_info.variables:
                text += '## Variables\n'
                for var in module_info.variables:
                    if var.name.startswith('_'):
                        continue
                    # text += render_variable_info(var, truncate_at=10) + '\n'
                    text += render_variable_section(var)

            if module_info.functions:
                text += '## Functions\n'
                for function_info in [m for m in module_info.functions if not m.name.startswith('_')]:
                    text += render_function_section(function_info)

            if module_info.examples:
                text += '## Examples\n'
                for example in module_info.examples:
                    text += dedent(f'''\
{example.name}
```
{example.content}
```
''')
            for separate_example_file in Path('.').glob(f'{module_info.name}_example*.py'):
                print('found external example:', separate_example_file)
                with separate_example_file.open('r') as f:
                    text += dedent(f'''\
{separate_example_file.stem}
```
{f.read()}
```
''')


        ### classes ###
        elif name in class_infos or name in singleton_infos:
            is_singleton = name in singleton_infos
            if is_singleton:
                name = snake_to_camel(name).title()

            class_info = class_infos[name]

            if is_singleton:
                name = class_info.module.name

            text += render_url_section(class_info.module.path)

            base_classes_text = ''
            base_classes_in_repo = [bcls for bcls in class_info.base_classes if bcls in pages]
            if base_classes_in_repo and not is_singleton:
                text += '<gray>Inherits</gray> '
                for bcls in base_classes_in_repo:
                    text += f'<a href="{camel_to_snake(bcls)}.html">{bcls}</a>'
                text += '\n'

            if Path(f'images/{name}.webp').exists():
                text += f'#image ../images/{name}.webp\n'

            class_variables= [e for e in class_info.class_variables if not e.name.startswith('_')] # ignore functions starting with underscore (_)
            if class_variables:
                text += '\n## Class Variables\n'
                for var in class_variables:
                    text += render_variable_section(var)

            ### __init__###
            init_methods = [m for m in class_info.methods if m.name == '__init__']
            init_method = init_methods[0] if init_methods else None
            if init_method:
                if not is_singleton:
                    text += dedent(f'''\

## Initialization
```
{class_info.name}{render_function_info(init_method).lstrip('__init__')}
```
                    ''')

                ### attributes (.self) ###
                public_attributes = [e for e in class_info.instance_variables if not e.name.startswith('_')]

                # remove cases with self.some_var = some_var
                public_attributes = [e for e in public_attributes if e.default_value != e.name or e.comment]

                if public_attributes:
                    text += dedent('''\

                        ## Attributes
                    ''')
                for var in public_attributes:
                    text += render_variable_section(var)

            # for m in class_info.methods:
            #     print(m.decorators)

            getters = [m for m in class_info.methods if m.name.endswith('_getter') or 'property' in m.decorators]
            setters = [m for m in class_info.methods if m.name.endswith('_setter') or f'{m.name}.setter' in m.decorators]

            # remove '_getter' and '_setter' from properties made ursina the property generator
            for e in getters:
                if e.name.endswith('_getter'):
                    e.base_name = e.name[:-len('_getter')]
                else:
                    e.base_name = e.name

            for e in setters:
                if e.name.endswith('_setter'):
                    e.base_name = e.name[:-len('_setter')]
                else:
                    e.base_name = e.name

            getters_only = [m for m in getters if m.base_name not in [p.base_name for p in setters]]
            two_way_properties = [m for m in setters if m.base_name not in [p.base_name for p in getters_only]]



            if getters_only:
                text += '\n## Getters\n'
            for method_info in getters_only:
                text += render_property_section(method_info)

            if two_way_properties:
                text += dedent('''\


                    ## Properties
                    ''')
            for method_info in two_way_properties:
                text += render_property_section(method_info)



            public_methods = [m for m in class_info.methods if not m.name.startswith('_') and m not in getters and m not in setters]
            if public_methods:
                text += '## Methods\n'
                for method_info in public_methods:
                    text += render_function_section(method_info) + '\n'

            if class_info.examples:
                # print('EXAMPLE::::')
                text += '## Examples\n'
                for example in class_info.examples:
                    text += dedent(f'''\
{example.name}
```
{example.content}
```
# ''')
            for separate_example_file in Path('.').glob(f'{class_info.name}_example*.py'):
                example_name = separate_example_file.stem.split('example')[1]
                print('found external example:', separate_example_file, example_name)
                if not example_name:
                    example_name = 'Example'
                text += f'{example_name}\n'

                with separate_example_file.open('r') as f:
                    text += f'''\
```
{f.read()}
```
'''

        # convert sswg to html without having to save it to disk first
        path = output_folder / f'{camel_to_snake(name)}.sswg'
        with path.open('w') as f:
            f.write(text)
            print('saved:', path)
            # if name == 'DirectionalLight':
            #     print('---------------------------------', text)

        # add sidebar
        sidebar_content = '<div class="sidebar">'
        sidebar_content += f'`{package_version}`'
        for group_name, group in groups.items():
            sidebar_content += f'\n{group_name}\n'
            for page_name in group:
                sidebar_content += f'  <a href="{camel_to_snake(page_name)}.html">{page_name}</a>\n'
        sidebar_content += '</div>'
        # with open('api_reference_sidebar.sswg', 'w') as f:
        #     f.write(sidebar_content)
        text += sidebar_content

        html_content = sswg.sswg_to_html(text, title=name)
        html_content = html_content.replace('href="sswg.css">', 'href="../sswg.css">')
        html_content = html_content.replace('href="style.css">', 'href="../style.css">')
        html_content += dedent('''\
            <style>
            h1 {margin-bottom:0em; margin-top:1em}
            h2 {margin-bottom:.5em;}
            h3 {margin:0em; font-size:1em;}
            code_block {margin-top:.0em; margin-bottom:1em;}
            hr {border-color:gray; opacity:.25;}
            .links {width:fit-content;}
            .links a {text-decoration:none; opacity:.5;}
            </style>
            ''')

        path = output_folder / f'{camel_to_snake(name)}.html'
        with path.open('w') as f:
            f.write(html_content)

        # print('saved:', path)


    # samples
    # generate sample pages:
    samples_folder = application.package_folder.parent / 'samples'
    generated_sample_pages = dict()

    for sample_name in ('Tic Tac Toe', 'Inventory', 'Pong', 'Minecraft Clone', "Rubik's Cube", 'Clicker Game', 'Platformer', 'FPS', 'Particle System', 'Column Graph'):
        file_name = sample_name.replace(' ','_').replace('\'','').lower() + '.py'
        file_path = samples_folder / file_name
        image_path = Path(f'icons/{file_path.stem}.jpg')
        image_code = ''
        image_url = f'icons/{file_path.stem}.jpg'
        github_link = f'https://github.com/pokepetter/ursina/tree/{version_tag}/samples/{file_name}'
        if image_path.exists():
            image_code = f'#image {image_url}'
        else:
            image_code = '#image icons/installation_guide.jpg'
            print('no image:', image_path)

        if file_path.exists():
            print(f'generate webpage for: {sample_name} -> {file_path.stem}.html')
            with open(file_path, 'r') as source_file:
                source_code = source_file.read()

            with open(f'{file_path.stem}.html', 'w') as file:
                file.write(sswg.sswg_to_html(
                        textwrap.dedent(f'''\
                        #title ursina engine documentation
                        #insert menu.sswg

                        ### {sample_name}
                        <a href="{github_link}">{github_link}</a>

                        {image_code}
                        ```\n''')
                        + source_code
                        + '\n```'
                    )
                )
                generated_sample_pages[sample_name] = (f'{file_path.stem}.html', image_url)
        else:
            print('sample not found:', file_path)

    samples_page_content = dedent('''\
        #title ursina engine samples
        #insert menu.sswg

        ### Samples
        ## Single File
        ''')
    for name, urls in generated_sample_pages.items():
        html_url, image_url = urls
        samples_page_content += f'[{name}, {html_url}, {image_url}]\n'

    samples_page_content += dedent('''\
        ## Projects
        [Value of Life, https://github.com/pokepetter/ld44_life_is_currency, icons/value_of_life_icon.jpg]
        [Castaway, https://github.com/pokepetter/pyweek_30_castaway, icons/castaway_icon.jpg]
        [Protein Visualization, https://github.com/HarrisonTCodes/ursina-proteins, icons/protein_visualization_icon.jpg]
        ''')
    with open('samples.sswg', 'w') as f:
        f.write(samples_page_content)
