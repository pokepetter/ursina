from direct.showbase.ShowBase import ShowBase
from panda3d.core import Lens
from panda3d.core import LensNode
from panda3d.core import PerspectiveLens
from panda3d.core import OrthographicLens
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.task.Task import Task
from panda3d.core import NodePath
from panda3d.core import PandaNode
from panda3d.core import Vec3
from panda3d.core import Point3
from panda3d.core import loadPrcFileData
from panda3d.core import Filename
from panda3d.core import AntialiasAttrib

import sys
import os
import math
import random
import inspect
import importlib
import re
import subprocess

import undo
from undo import undoable
undo.setstack(undo.Stack())
# from PIL import Image     # for texture compression, editor.py
# from tinyblend import BlenderFile     # for .blend import, editor.py

import application
from entity import Entity
import scene
import mouse
import keys
from keys import held_keys
import camera
import window
import debug
import color

import main

sys.path.append("..")
path = Filename.toOsSpecific(application.internal_prefab_folder)
sys.path.insert(0, path)



def distance(a, b):
    return math.sqrt(sum( (a - b)**2 for a, b in zip(a, b)))

# def save_scene():
    # has_scene_entity = False
    # for e in scene.entities:
    #     if e.name.startswith('scene') and e.parent == scene.render:
    #         scene_entity = e
    #         has_scene_entity = True
    #         break
    # if not has_scene_entity:
    #     scene_entity = Entity()
    #     scene_entity.name = name
    #
    # for e in scene.entities:
    #     if not e.is_editor and e.parent == scene.render and e is not scene_entity:
    #         print(e)
    #         e.parent = parent_entity

    # save_prefab(scene_entity, name)

    # for e in scene.entities:
        # if e.parent = parent_entity


def save_prefab(target, path='prefabs'):
    prefab_path = os.path.join(
        path,
        target.name + '_' + str(target.get_key()) + '.py')

    with open(prefab_path, 'w') as file:

        file.write('import sys\n')
        file.write('sys.path.append("..")\n')
        file.write('from pandaeditor import *\n\n')

        file.write('class ' + target.name.title() + '_' + str(target.get_key()) + '(Entity):\n\n')
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

def vec3_to_string(vec3):
    string = '(' + str(round(vec3[0], 3)) + ', ' + str(round(vec3[1], 3))
    if vec3[2] is not 0:
        string += ', ' + str(round(vec3[2]), 3)
    string += ')'
    return string


def load_prefab(module_name, add_to_caller=False):
    paths = ('internal_prefabs.', '..prefabs.')
    prefab = load(paths, module_name)
    # if hasattr(caller, 'name') and caller.name == 'editor':
    #     prefab.is_editor = True
    if add_to_caller:
        caller = inspect.currentframe().f_back.f_locals['self']
        try: prefab.parent = caller.model
        except:
            try: prefab.parent = caller
            except: pass

    return prefab

def load_scene(module_name):
    file_name = module_name + '.py'
    module_names = (os.path.join(os.path.dirname(__file__), file_name),
                    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scenes', file_name),
                    os.path.join(os.path.dirname(__file__), 'internal_scenes', file_name)
                    )

    for name in module_names:
        try:
            module = importlib.machinery.SourceFileLoader(module_name, name).load_module()

            print('name:', snake_to_camel(module_name))
            try:
                class_ = getattr(module, snake_to_camel(module_name))
            except:
                # load first class
                class_names = inspect.getmembers(sys.modules[module_name], inspect.isclass)
                for cn in class_names:
                    if cn[1].__module__ == module.__name__:
                        class_ = getattr(module, cn[0])
                        break
            class_instance = class_()
            class_instance.parent = scene
            destroy(scene.entity)
            scene.entity = class_instance
            print('found scene:', name)
            # print(scene.entity.name)
            return class_instance
            break
        except Exception as e:
            print(e)

    print("couldn't find scene:", module_name)

def load_script(module_name):
    paths = ('internal_scripts.', '..scripts.')
    return load(paths, module_name)



def load(paths, module_name):
    if inspect.isclass(module_name):
        class_instance = module_name()
        # print('added script:', class_instance)
        return class_instance

    # find the module
    module = None
    for f in paths:
        # print('mod:', f + module_name)
        try:
            module = importlib.import_module(f + module_name)
            break
        except:
            pass

    if not module:
        print(module_name, 'not found')
        return
    # else:
    #     print('class:', inspect.getmembers(sys.modules[module.__name__], inspect.isclass)[0])

    # load its class
    class_names = inspect.getmembers(sys.modules[module.__name__], inspect.isclass)
    for cn in class_names:
        if cn[1].__module__ == module.__name__:
            class_name = cn[0]
            break

    class_ = getattr(module, class_name)
    class_instance = class_()

    # print('added script:', class_instance)
    return class_instance


def destroy(entity):
    scene.entities.remove(entity)
    try: entity.model.removeNode()
    except: pass
    try:
        entity.removeAllChildren()
        entity.removeNode()
    except: pass
    try: entity.texture.releaseAll()
    except: pass
    try:
        del entity
    except: pass


def raycast(origin, direction, distance):
    pFrom = Point3(origin[0], origin[1], origin[2])
    pTo = Point3(origin[0], origin[1], origin[2]) + (direction * distance)
    print('to', pTo)

    result = scene.world.rayTestClosest(pFrom, pTo)


import operator
def size_list():
    #return a list of current python objects sorted by size
    globals_list = list()
    globals_list.clear()
    for e in globals():
        # object, size
        globals_list.append([e, sys.getsizeof(e)])
    globals_list.sort(key=operator.itemgetter(1), reverse=True)
    print('scene size:', globals_list)


def clamp(value, floor, ceiling):
    return max(min(value, ceiling), floor)


def camel_to_snake(value):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(value):
    camel = ''
    words = value.split('_')
    for w in words:
        camel += w.title()
    return camel


def count_lines(file):
    all_lines = 0
    blank_lines = 0
    comment_lines = 0
    used_lines = 0

    with open(file) as f:
        for line in f:
            all_lines += 1

            if len(line.strip()) == 0:
                blank_lines += 1

            if line.strip().startswith('#'):
                comment_lines += 1
    print('all_lines:', all_lines)
    print('blank_lines:', blank_lines)
    print('comment_lines:', comment_lines)
    print('used_lines:', all_lines - blank_lines - comment_lines)


def chunk_list(l, cunk_size):
    # yield successive chunks from list
    for i in range(0, len(l), cunk_size):
        yield l[i:i + cunk_size]
