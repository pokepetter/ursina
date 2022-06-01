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
from ursina.text import Text
from ursina.window import instance as window
from ursina.scene import instance as scene
from ursina.sequence import Sequence, Func, Wait


class Empty():
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key ,value)



def invoke(function, *args, **kwargs):
    delay = 0
    if 'delay' in kwargs:
        delay = kwargs['delay']
        del kwargs['delay']

    if not delay:
        function(*args, **kwargs)
        return function

    s = Sequence(
        Wait(delay),
        Func(function, *args, **kwargs)
    )
    s.start()
    return s


def destroy(entity, delay=0):
    if delay == 0:
        _destroy(entity)
        return

    s = Sequence(
        Wait(delay),
        Func(_destroy, entity)
    )
    s.start()
    return s

def _destroy(entity, force_destroy=False):
    from ursina import camera
    if not entity or entity == camera:
        return

    if entity.eternal and not force_destroy:
        return

    if hasattr(entity, 'stop'):
        entity.stop(False)
        # return

    if hasattr(entity, 'on_destroy'):
        entity.on_destroy()

    for c in entity.children:
        _destroy(c)

    if entity in scene.entities:
        scene.entities.remove(entity)


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

    try:
        entity.removeNode()
    except:
        print('already destroyed')
    #unload texture
    # if hasattr(entity, 'texture') and entity.texture != None:
    #     entity.texture.releaseAll()

    del entity


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
    text_entity = Text(text=text, position=position, origin=origin, scale=scale)
    destroy(text_entity, delay=duration)


class LoopingList(list):
    def __getitem__(self, i):
        return super().__getitem__(i % len(self))



if __name__ == '__main__':

    from ursina import *
    app = Ursina()
    def test_func(item, x=None, y=None):
        print(item, x, y)

    test_func('test')
    invoke(test_func, 'test', delay=.1)
    invoke(test_func, 'test1', 1, 2, delay=.2)
    invoke(test_func, 'test2', x=1, y=2, delay=.3)

    def input(key):
        if key == 'space':
            print_on_screen('debug message', position=(0,0), origin=(0,0), scale=2)


    app.run()
