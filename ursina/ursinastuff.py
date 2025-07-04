import sys
import os

from ursina import application
from ursina.scene import instance as scene
from ursina.sequence import Sequence, Func, Wait


class Empty():
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key ,value)

class DotDict(dict):
    """Custom dictionary class to allow dot notation access."""
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(f"'DotDict' object has no attribute '{attr}'")

    def __setattr__(self, attr, value):
        self[attr] = value

    def __delattr__(self, attr):
        try:
            del self[attr]
        except KeyError:
            raise AttributeError(f"'DotDict' object has no attribute '{attr}'")


class Default:
    pass


def invoke(function, *args, **kwargs):  # reserved keywords: 'delay', 'unscaled'
    delay = 0
    if 'delay' in kwargs:
        delay = kwargs['delay']
        del kwargs['delay']

    unscaled = False
    if 'unscaled' in kwargs:
        unscaled = kwargs['unscaled']
        del kwargs['unscaled']

    ignore_paused = False
    if 'ignore_paused' in kwargs:
        ignore_paused = kwargs['ignore_paused']
        del kwargs['ignore_paused']

    if not delay:
        function(*args, **kwargs)
        return None

    if ignore_paused:
        unscaled = True

    return Sequence(
        Wait(delay),
        Func(function, *args, **kwargs),
        auto_destroy=True, ignore_paused=ignore_paused, unscaled=unscaled, started=True,
    )


def after(delay, unscaled=True, ignore_paused=False, entity=None):    # function for @after decorator. Use the decorator, not this.
    '''@after decorator for calling a function after some time.

        example:
        @after(.4)
        def reset_cooldown():
            self.on_cooldown = False
            self.color = color.green
    '''
    def _decorator(func):
        def wrapper(*args, **kwargs):
            sequence = invoke(func, *args, **kwargs, delay=delay, unscaled=unscaled, ignore_paused=ignore_paused)
            if entity is not None:
                entity.animations.append(sequence)

        return wrapper()
    return _decorator



def destroy(entity, delay=0, unscaled=True, ignore_paused=False):
    if application.development_mode:
        # get the calling function and the file it's from, so we can give a better error message if we try to use it after destroy
        entity.destroy_source = f'caller: {sys._getframe(1).f_code.co_name} file: {sys._getframe(1).f_code.co_filename}'

    if delay == 0:
        _destroy(entity)
        return True

    return invoke(_destroy, entity, delay=delay, unscaled=unscaled, ignore_paused=ignore_paused)
    # return Sequence(Wait(delay), Func(_destroy, entity), auto_destroy=True, started=True)


def _destroy(entity, force_destroy=False):
    # from ursina import camera
    # if not entity or entity == camera:
    #     return

    if entity.eternal and not force_destroy:
        return

    if hasattr(entity, 'scripts'):
        for s in entity.scripts:
            del s

    if hasattr(entity, 'animations'):
        for anim in entity.animations:
            anim.kill()

    for child in entity.children:
        _destroy(child)

    if entity.collider:
        entity.collider.remove()

    if hasattr(entity, 'clip') and hasattr(entity, 'stop'): # stop audio
        entity.stop(False)

    if hasattr(entity, 'on_destroy'):
        entity.on_destroy()

    if entity in scene.entities:
        scene.entities.remove(entity)

    if entity in scene.collidables:
        scene.collidables.remove(entity)

    if hasattr(entity, '_parent') and entity._parent and hasattr(entity._parent, '_children') and entity in entity._parent._children:
        entity._parent._children.remove(entity)

    for e in entity.loose_children:
        destroy(e)

    if hasattr(entity, '_loose_parent') and entity._loose_parent and hasattr(entity._loose_parent, '_loose_children') and entity in entity._loose_parent._loose_children:
        entity._loose_parent._loose_children.remove(entity)

    if hasattr(entity, 'tooltip'):
        _destroy(entity.tooltip)

    if hasattr(entity, '_on_click') and isinstance(entity._on_click, Sequence):
        entity._on_click.kill()

    if entity.hasPythonTag("Entity"):
        entity.clearPythonTag("Entity")

    entity.removeNode()

    if hasattr(entity.__class__, 'instances') and entity in entity.__class__.instances:
        entity.__class__.instances.remove(entity)
    #unload texture
    # if hasattr(entity, 'texture') and entity.texture != None:
    #     entity.texture.releaseAll()

    del entity



def size_list():    # return a list of current python objects sorted by size
    import operator

    globals_list = []
    globals_list.clear()
    for e in globals():
        # object, size
        globals_list.append([e, sys.getsizeof(e)])
    globals_list.sort(key=operator.itemgetter(1), reverse=True)
    print('scene size:', globals_list)


def find_sequence(name, file_types, folders): # find frame_0, frame_1, frame_2 and so on
    for folder in folders:
        for file_type in file_types:
            files = list(folder.glob(f'**/{name}*.{file_type}'))
            if files:
                files.sort()
                return files
    return []


def import_all_classes(path=application.asset_folder, debug=False):
    path = str(path)
    sys.path.append(path)
    from ursina.string_utilities import snake_to_camel
    from glob import iglob
    imported_successfully = []

    for file_path in iglob(path + '**/*.py', recursive=True):
        if '\\build\\' in file_path or '__' in file_path:
            continue

        rel_path = file_path[len(path):][:-3].replace('\\', '.')
        if rel_path.startswith('.'):
            rel_path = rel_path[1:]
        module_name = os.path.basename(file_path).split('.')[0]
        # class_name = snake_to_camel(module_name)
        module_name = module_name
        import_statement = 'from ' + rel_path + ' import *'

        try:
            exec(import_statement, globals())
            imported_successfully.append(module_name)
            if debug:
                print(import_statement)
        except:
            if debug:
                print('     x', import_statement)
            pass

    return imported_successfully


def print_on_screen(text, position=(0,0), origin=(-.5,.5), scale=1, duration=1, color=(1,1,1,1)):
    from ursina.text import Text
    text_entity = Text(text=text, position=position, origin=origin, scale=scale, color=color)
    destroy(text_entity, delay=duration)


import traceback
from inspect import getframeinfo, stack
import ast
import textwrap
import inspect

def _test(result):
    if callable(result):
        result = result()

    caller_frame = stack()[1][0]
    caller_info = getframeinfo(caller_frame)
    filename, lineno = caller_info.filename, caller_info.lineno

    # Get full multi-line _test call source
    source_lines, starting_line_no = inspect.getsourcelines(caller_frame)
    rel_lineno = lineno - starting_line_no
    lines = source_lines[rel_lineno:]
    call_text = ""
    parens = 0
    started = False
    for line in lines:
        stripped = line.strip()
        if not started and stripped.startswith("_test"):
            started = True
        if started:
            call_text += line
            parens += line.count("(") - line.count(")")
            if parens <= 0:
                break
    call_text = textwrap.dedent(call_text)

    try:
        tree = ast.parse(call_text, mode='exec')
        call = tree.body[0].value  # _test(...)
        arg_source = ast.unparse(call.args[0])
    except Exception:
        arg_source = "<expression>"

    def extract_func_name(expr_ast):
        if isinstance(expr_ast, ast.Call):
            return extract_func_name(expr_ast.func)
        elif isinstance(expr_ast, ast.Attribute):
            value = extract_func_name(expr_ast.value)
            return f"{value}.{expr_ast.attr}"
        elif isinstance(expr_ast, ast.Name):
            return expr_ast.id
        else:
            return "<unknown>"

    try:
        expr_ast = ast.parse(arg_source, mode='eval').body
        if isinstance(expr_ast, ast.Compare):
            func_name = extract_func_name(expr_ast.left)
        else:
            func_name = extract_func_name(expr_ast)
    except Exception:
        func_name = "<unknown>"

    MAX_LEN = 32
    display_expr = (arg_source[:MAX_LEN] + '...') if len(arg_source) > MAX_LEN else arg_source

    if result:
        print(f'\33[42mPASSED\033[0m {func_name} {display_expr}')
        return True
    else:
        print(f'\33[41mFAILED\033[0m {func_name} {display_expr}')
        print(f' --> {filename}:{lineno}')
        print("Stack trace (most recent call last):")
        traceback.print_stack(f=caller_frame)
        return False




# define a new metaclass which overrides the "__call__" function
class PostInitCaller(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj.__post_init__()
        return obj

if __name__ == '__main__':

    from ursina import *
    app = Ursina()





    a = Audio('sine')
    a.play()
    destroy(a, delay=1)
    # Player()
    app.run()
