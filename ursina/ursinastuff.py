import sys
import os
import math
import random
import inspect
import importlib
import subprocess
import time
from pathlib import Path

from ursina import application
from ursina.scene import instance as scene
from ursina.sequence import Sequence, Func, Wait


class Empty():
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key ,value)

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

    if not delay:
        function(*args, **kwargs)
        return None

    s = Sequence(
        Wait(delay),
        Func(function, *args, **kwargs)
    )
    s.unscaled = unscaled
    s.start()
    return s


def after(delay, unscaled=True):
    '''@after  decorator for calling a function after some time.

        example:
        @after(.4)
        def reset_cooldown():
            self.on_cooldown = False
            self.color = color.green
    '''
    def decorator(func):
        def wrapper(*args, **kwargs):
            invoke(func, *args, **kwargs, delay=delay, unscaled=unscaled)
        return wrapper()
    return decorator



def get_class_name(func):
    qualname_parts = func.__qualname__.split('.')
    class_name = qualname_parts[-2] if len(qualname_parts) > 1 else None
    return class_name

class every:
    '''@after  decorator for calling a function on an Entity after some time.

        example:
        @every(.1)
        def fixed_update():
            print('check collision')

        Using the @every decorator is the same as doing this in __init__() (on Entity):
        self.animations.append(Sequence(Func(self.fixed_update), Wait(.1), loop=True, started=True))
        The Sequence will call the function every .1 second, while adding it to
        self.animations ensures the Sequence gets cleaned up when the Entity gets destroyed.
    '''
    decorated_methods = []  # store decorated methods here

    def __init__(self, interval):
        self.interval = interval

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # print(f"Calling {func.__name__} every {self.interval} seconds")
            return func(*args, **kwargs)

        wrapper._every = self  # add _every attribute to the decorated method
        wrapper._func = func
        every.decorated_methods.append(wrapper)  # store the decorated method
        return wrapper



def destroy(entity, delay=0):
    if delay == 0:
        _destroy(entity)
        return

    s = Sequence(Wait(delay), Func(_destroy, entity))
    s.start()
    return s

def _destroy(entity, force_destroy=False):
    from ursina import camera
    if not entity or entity == camera:
        return

    if entity.eternal and not force_destroy:
        return

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


    if hasattr(entity, 'scripts'):
        for s in entity.scripts:
            del s

    if hasattr(entity, 'animations'):
        for anim in entity.animations:
            anim.finish()
            anim.kill()

    if hasattr(entity, 'tooltip'):
        _destroy(entity.tooltip)

    if hasattr(entity, '_on_click') and isinstance(entity._on_click, Sequence):
        entity._on_click.kill()

    entity.removeNode()
    #unload texture
    # if hasattr(entity, 'texture') and entity.texture != None:
    #     entity.texture.releaseAll()

    del entity



def chunk_list(l, chunk_size):
    # yield successive chunks from list
    for i in range(0, len(l), chunk_size):
        yield l[i:i + chunk_size]


def flatten_list(l):
    # return [item for sublist in l for item in sublist]
    import itertools
    return list(itertools.chain(*l))

def flatten_completely(container):
    for i in container:
        if isinstance(i, (list,tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i



def size_list():
    #return a list of current python objects sorted by size
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
        class_name = snake_to_camel(module_name)
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


def print_on_screen(text, position=(0,0), origin=(-.5,.5), scale=1, duration=1):
    from ursina.text import Text
    text_entity = Text(text=text, position=position, origin=origin, scale=scale)
    destroy(text_entity, delay=duration)


class LoopingList(list):
    def __getitem__(self, i):
        return super().__getitem__(i % len(self))



if __name__ == '__main__':

    from ursina import *
    app = Ursina()



    # Player()
    app.run()
