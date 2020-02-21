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


def save_prefab(target, name=None, path='prefabs'):
    if not name:
        name = target.name

    prefab_path = os.path.join(
        path,
        target.name + '_' + str(target.get_key()) + '.py')

    with open(prefab_path, 'w') as file:
        file.write('from ursina import *\n\n')

        file.write('class ' + name.title() + '_' + str(target.get_key()) + '(Entity):\n\n')
        file.write('    def __init__(self):\n')
        file.write('        super().__init__()\n')

        entities_to_save = list()
        entities_to_save.append(target)
        for e in scene.entities:
            if e.has_ancestor(target):
                entities_to_save.append(e)

        for e in entities_to_save:
            if e is target:
                prefix = '        self'
            else:
                prefix = '        self.' + e.name + '_' + str(e.get_key())

            color_str = ('(' + str(e.color[0]) + ', '
                            + str(e.color[1]) + ', '
                            + str(e.color[2]) + ', '
                            + str(e.color[3]) + ')')

            palette = [item for item in dir(color) if not item.startswith('__')]
            for colorname in palette:
                if getattr(color, colorname) == e.color:
                    color_str = 'color.' + colorname
                    break

            if e is not target:
                file.write(prefix + ' = Entity()' + '\n')

            parent_str = 'self.' + e.parent.name + '_' + str(e.parent.get_key())
            if e.parent == target:
                parent_str = 'self'

            file.write(prefix + '.enabled = ' + str(e.enabled) + '\n'
                + prefix + '.is_editor = ' + str(e.is_editor) + '\n'
                + prefix + '.name = ' + '\'' + str(e.name) + '\'' + '\n'
                + prefix + '.parent = ' + parent_str + '\n')

            if e.origin != Vec3(0,0,0):
                file.write(prefix + '.origin = ' + vec3_to_string(e.origin) + '\n')
            if e.position != Vec3(0,0,0):
                file.write(prefix + '.position = ' + vec3_to_string(e.position) + '\n')
            if e.rotation != Vec3(0,0,0):
                file.write(prefix + '.rotation = ' + vec3_to_string(e.rotation) + '\n')
            if e.scale != Vec3(1,1,1):
                file.write(prefix + '.scale = ' + vec3_to_string(e.scale) + '\n')

            if e.model:
                file.write(prefix + '.model = ' + '\'' + os.path.basename(str(e.model))[:4] + '\'' + '\n')
            if e.color:
                file.write(prefix + '.color = ' + color_str + '\n')
            if e.texture:
                file.write(prefix + '.texture = ' + str(e.texture) + '\n')

            file.write(prefix + '.collision = ' + str(e.collision) + '\n')
            if e.collider:
                file.write(prefix + '.collider = ' + str(e.collider) + '\n')





            for s in e.scripts:
                if e is target:
                    script_prefix = prefix + '.' + str(s.__class__.__name__).lower()
                else:
                    script_prefix = prefix + '_' + str(s.__class__.__name__).lower()

                file.write(script_prefix + ' = ' + prefix[8:] + '.add_script(\'' + s.__class__.__name__ + '\')\n')

                for var in [item for item in vars(s) if not item.startswith('_')]:

                    varvalue = getattr(s, var)

                    if not varvalue:
                        continue

                    print(type(varvalue))

                    if varvalue.__class__ == Entity:
                        if varvalue is target:
                            varvalue = 'self'
                        else:
                            varvalue = str(varvalue.name) + '_' + str(varvalue.get_key())

                    print('hyhrh')
                    file.write(script_prefix + '.' + var + ' = ' + str(varvalue) + '\n')

        print('saved prefab:', path, target.name)

def _vec3_to_string(vec3):
    string = '(' + str(round(vec3[0], 3)) + ', ' + str(round(vec3[1], 3))
    if vec3[2] is not 0:
        string += ', ' + str(round(vec3[2]), 3)
    string += ')'
    return string


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
def print_on_screen(text):
    text_entity = Text(
        # parent = camera.ui,
        text = str(text),
        position = window.top_left,
        origin = (-.5, .5),
        # scale = (.1, .1)
        )
    destroy(text_entity, 1)


if __name__ == '__main__':

    from ursina import *
    app = Ursina()
    def test_func(item, x=None, y=None):
        print(item, x, y)

    test_func('test')
    invoke(test_func, 'test', delay=.1)
    invoke(test_func, 'test1', 1, 2, delay=.2)
    invoke(test_func, 'test2', x=1, y=2, delay=.3)

    app.run()
