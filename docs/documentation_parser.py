import ast
import importlib
import pkgutil
import textwrap
import tokenize
import tomllib
from io import StringIO
from pathlib import Path

from ursina.string_utilities import snake_to_camel


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
    module_info.is_singleton = is_singleton(source_code, path.stem) if path is not None else False

    for node in tree.body:
         # module level variables
        if isinstance(node, ast.Assign | ast.AnnAssign):
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



def get_all_modules_in_package(package):
    modules = []
    for _importer, modname, _ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            # print('Importing:', modname)
            module = importlib.import_module(modname)
            modules.append(module)
        except Exception as e:
            print(f"Failed to import {modname}: {e}")
    return modules


if __name__ == '__main__':
    from ursina import application
    # with open(application.package_folder / 'application.py', 'r') as f:
    path = application.package_folder / 'entity.py'
    with path.open('r') as f:
        module_info = analyze_module(f.read())

    print('module name:', module_info.name)
    print('--- module variables ---')
    for e in module_info.variables:
        # print('module level var:', e)
        if e.name.startswith('_'):
            continue
        type_hint = f': {e.type_hint}' if e.type_hint is not None else ''
        print(f'    {e.name} {type_hint}= {e.default_value}')

    print('--- module functions ---')
    for function_info in module_info.functions:
        print(function_info)

    for class_info in module_info.classes:
        print('--- class ---')
        print(f'class: {class_info.name}({', '.join(class_info.base_classes)})')
        print('--- class_variables ---')
        for e in class_info.class_variables:
            if e.name.startswith('_'):
                continue
            # print(f'    {class_info.name}.{e.name} = ')
            type_hint = f': {e.type_hint}' if e.type_hint is not None else ''
            print(f'    {e.name} {type_hint}= {e.default_value}')

        print('--- init ---')
        print(f'{class_info.name}(')
        for e in class_info.init_args:
            if e.name.startswith('_'):
                continue
            type_hint = f': {e.type_hint}' if e.type_hint is not None else ''
            print(f'    {e.name} {type_hint}= {e.default_value}')
        print('    )')

        print('--- properties ---')
        for e in class_info.properties:
            print('   ', e)
        # print('args:', class_info.init_args)

