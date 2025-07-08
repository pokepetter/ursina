from pathlib import Path
from textwrap import dedent

import sswg
from documentation_parser import VarInfo, analyze_module, get_all_modules_in_package, get_package_version

import ursina
from ursina import application, camel_to_snake, flatten_list, print_warning, snake_to_camel


def generate_documentation():
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


    modules = [ursina, ] + get_all_modules_in_package(ursina)

    module_infos = dict()
    for mod in modules:
        with open(mod.__file__) as f:
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

    for _module_name, modinf in module_infos.items():
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
        text += '<hr></hr>\n'
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
            module_info.variables = [var for var in module_info.variables if not var.name.startswith('_')]

            if Path(f'images/{name}.webp').exists():
                text += f'#image ../images/{name}.webp\n'

            if module_info.variables:
                text += '## Variables\n'
                for var in module_info.variables:
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
{class_info.name}{render_function_info(init_method).replace('__init__', '')}
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
            base_name = class_info.name
            if class_info.module.is_singleton:
                base_name = camel_to_snake(base_name)

            external_examples = list(Path('.').glob(f'{base_name}_example*.py'))
            if len(external_examples) > 0 and not class_info.examples:
                text += '## Examples\n'

            for separate_example_file in external_examples:
                example_name = separate_example_file.stem.split('example')[1]
                example_name = example_name.lstrip('_')
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

        # # convert sswg to html without having to save it to disk first
        # path = output_folder / f'{camel_to_snake(name)}.sswg'
        # with path.open('w') as f:
        #     f.write(text)
        #     print('saved:', path)

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

    for sample_name in ('Tic Tac Toe', 'Inventory', 'Pong', 'Minecraft Clone', "Rubik's Cube", 'Clicker Game', 'Platformer', 'FPS', 'Column Graph'):
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
            # print(f'generate webpage for: {sample_name} -> {file_path.stem}.html')
            with file_path.open() as source_file:
                source_code = source_file.read()

            with open(f'{file_path.stem}.html', 'w') as file:
                file.write(sswg.sswg_to_html(
                        dedent(f'''\
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


if __name__ == '__main__':
    generate_documentation()