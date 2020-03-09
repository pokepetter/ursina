from direct.showbase.ShowBase import ShowBase
from panda3d.core import Lens, LensNode, PerspectiveLens, OrthographicLens
# from direct.interval.IntervalGlobal import Sequence, Func, Wait, SoundInterval
from ursina.sequence import Sequence, Func, Wait
from direct.interval.IntervalGlobal import SoundInterval
from direct.task.Task import Task
from panda3d.core import NodePath, PandaNode
from panda3d.core import Vec2
from ursina.vec3 import Vec3
from panda3d.core import loadPrcFileData, Filename, AntialiasAttrib
from panda3d.core import PNMImage, Texture

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
from ursina.entity import Entity
from ursina import scene
from ursina import window
from ursina import mouse
from ursina import camera
from ursina import raycaster
from ursina.raycaster import raycast, boxcast
from ursina import color
from ursina.input_handler import held_keys
from ursina import input_handler



def invoke(function, *args, **kwargs):
    delay = 0
    if 'delay' in kwargs:
        delay = kwargs['delay']
        del kwargs['delay']

    if not delay:
        function(*args, **kwargs)
        return function

    s = Sequence()
    s.append(Wait(delay))
    s.append(Func(function, *args, **kwargs))
    s.start()
    return s


def destroy(entity, delay=0):
    if delay == 0:
        _destroy(entity)
        return

    s = Sequence()
    s.append(Wait(delay))
    s.append(Func(_destroy, entity))
    s.start()

def _destroy(entity):
    if not entity:
        print('entity is None')
        return
    if entity in scene.entities:
        scene.entities.remove(entity)

    if hasattr(entity, 'on_destroy'):
        entity.on_destroy()

    if hasattr(entity, 'scripts'):
        for s in entity.scripts:
            del s

    if hasattr(entity, 'animations'):
        for anim in entity.animations:
            anim.finish()
            anim.kill()

    if hasattr(entity, 'tooltip'):
        destroy(entity.tooltip)
        # entity.tooltip.removeNode()

    entity.removeNode()

    #unload texture
    # if hasattr(entity, 'texture') and entity.texture != None:
    #     entity.texture.releaseAll()

    del entity


def import_all_classes(path=application.asset_folder, debug=False):
    path = str(path)
    sys.path.append(path)
    from ursina.string_utilities import snake_to_camel
    from glob import iglob
    imported_successfully = list()

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


from ursina.text import Text
def print_on_screen(text, position=window.top_left, origin=(-.5,.5), scale=1, duration=1):
    text_entity = Text(text=text, position=position, origin=origin, scale=scale)
    destroy(text_entity, delay=duration)

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
