from direct.showbase.ShowBase import ShowBase
from panda3d.core import Lens, LensNode, PerspectiveLens, OrthographicLens
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.task.Task import Task
from panda3d.core import NodePath, PandaNode
from panda3d.core import Vec2, Vec3, Point3
from panda3d.core import loadPrcFileData, Filename, AntialiasAttrib
from panda3d.core import PNMImage, Texture

import sys
import os
import math
import random
import inspect
import importlib
import re
import subprocess

# from PIL import Image     # for texture compression, editor.py
# from tinyblend import BlenderFile     # for .blend import, editor.py

from pandaeditor import application
from pandaeditor.entity import Entity
from pandaeditor import scene
from pandaeditor import window
from pandaeditor import mouse
from pandaeditor import input
from pandaeditor.input import held_keys
from pandaeditor import camera
from pandaeditor import raycaster
from pandaeditor.raycaster import raycast
from pandaeditor import debug
from pandaeditor import color
from pandaeditor import undo
from pandaeditor.undo import *
undo.setstack(undo.Stack())

from pandaeditor import main



def distance(a, b):
    return a.getDistance(b)
    # (point1.getXy() - point2.getXy()).length()


# def save_scene():
    # has_scene_entity = False
    # for e in scene.entities:
    #     if e.name.startswith('scene') and e.parent == render:
    #         scene_entity = e
    #         has_scene_entity = True
    #         break
    # if not has_scene_entity:
    #     scene_entity = Entity()
    #     scene_entity.name = name
    #
    # for e in scene.entities:
    #     if not e.is_editor and e.parent == render and e is not scene_entity:
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
    paths = (application.internal_prefab_folder, application.prefab_folder)
    prefab = None
    try:
        prefab = load(paths, module_name)
    except:
        print('MISSING PREFAB:', module_name)
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
    if inspect.isclass(module_name):
        class_instance = module_name()
        # scene =
        return class_instance


    paths = (application.internal_scene_folder, application.scene_folder)
    try:
        for e in scene.children:
            destroy(e)
    except:
        print('scene not yet initialized')
    prefab = load(paths, module_name)
    print('found scene:', module_name, 'prefab:', prefab)
    return prefab


def load_script(module_name):
    paths = (application.internal_script_folder, application.script_folder)
    return load(paths, module_name)



def load(paths, module_name):
    if inspect.isclass(module_name):
        class_instance = module_name()
        # print('added script:', class_instance)
        return class_instance

    # find the module
    module = None
    # module_name += '.py'
    import importlib.util

    for p in paths:
        # print('mod:', f + module_name)
        # try:
        if module_name + '.py' in os.listdir(p):
            spec = importlib.util.spec_from_file_location(module_name, p + module_name + '.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # load its class
            class_names = inspect.getmembers(module, inspect.isclass)
            for cn in class_names:
                if cn[1].__module__ == module.__name__:
                    class_name = cn[0]
                    break

            class_ = getattr(module, class_name)
            class_instance = class_()

            print('added script:', class_instance)
            return class_instance

def invoke(function, *args, **kwargs):
    s = Sequence()
    if 'delay' in kwargs:
        s.append(Wait(kwargs['delay']))
    s.append(Func(function, *args))
    s.start()


def destroy(entity, delay=0):
    if delay == 0:
        _destroy(entity)
        return

    s = Sequence()
    s.append(Wait(delay))
    s.append(Func(_destroy))
    s.start()

def _destroy(entity):
    if entity in scene.entities:
        scene.entities.remove(entity)

    if hasattr(entity, 'model') and entity.model != None:
        entity.model.removeNode()

    # entity.removeAllChildren()
    # try:

        entity.removeNode()
    # except:
    #     pass

    #unload texture
    # if hasattr(entity, 'texture') and entity.texture != None:
    #     entity.texture.releaseAll()

    del entity


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


def multireplace(string, replacements, ignore_case=False):
    """
    Given a string and a dict, replaces occurrences of the dict keys found in the
    string, with their corresponding values. The replacements will occur in "one pass",
    i.e. there should be no clashes.
    :param str string: string to perform replacements on
    :param dict replacements: replacement dictionary {str_to_find: str_to_replace_with}
    :param bool ignore_case: whether to ignore case when looking for matches
    :rtype: str the replaced string
    """
    rep_sorted = sorted(replacements, key=lambda s: len(s[0]), reverse=True)
    rep_escaped = [re.escape(replacement) for replacement in rep_sorted]
    pattern = re.compile("|".join(rep_escaped), re.I if ignore_case else 0)
    return pattern.sub(lambda match: replacements[match.group(0)], string)


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
    return all_lines


def chunk_list(l, cunk_size):
    # yield successive chunks from list
    for i in range(0, len(l), cunk_size):
        yield l[i:i + cunk_size]

def compress_textures():
    from PIL import Image
    from os.path import dirname
    files = os.listdir(application.texture_folder)
    compressed_files = os.listdir(application.compressed_texture_folder)

    for f in files:
        if f.endswith('.psd') or f.endswith('.png'):
            try:
                print('f:', application.compressed_texture_folder + '/' + f)

                image = Image.open(application.texture_folder + f)
                # print(max(image.size))
                if max(image.size) > 256:
                    image.save(
                        application.compressed_texture_folder + f[:-4] + '.jpg',
                        'JPEG',
                        quality=80,
                        optimize=True,
                        progressive=True
                        )
                    print('compressing to jpg:', f)
                else:
                    image.save(
                        application.compressed_texture_folder + f[:-4] + '.png',
                        'PNG'
                        )
                    print('compressing to png:', f)
            except:
                print('failed to compress:', f)
        # elif f.endswith('.png'):
