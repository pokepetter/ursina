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


import sys
import os
import math
import random
import inspect
import importlib

from entity import Entity
import scene
import mouse
import window
import camera
import debug
import color

from internal_scripts import *
# from internal_scenes import *
from internal_prefabs import *
sys.path.append("..")
from scripts import *
# from scenes import *
# from prefabs import *



def distance(a, b):
    return math.sqrt(sum( (a - b)**2 for a, b in zip(a, b)))

def save_scene(name):
    has_scene_entity = False
    for e in scene.entities:
        if e.name.startswith('scene') and e.parent == scene.render:
            scene_entity = e
            has_scene_entity = True
            break
    if not has_scene_entity:
        scene_entity = Entity()
        scene_entity.name = name

    for e in scene.entities:
        if not e.is_editor and e.parent == scene.render and e != scene_entity:
            print(e)
            e.parent = parent_entity
    save_prefab(scene_entity, name)
    # for e in scene.entities:
        # if e.parent = parent_entity


def save_prefab(entity, name):
    default_entity = Entity()
    default_entity.name = 'default_entity'
    defaults = default_entity.__dict__
    destroy(default_entity)
    attributes_to_ignore = (
        'x', 'y', 'z',
        'rotation_x', 'rotation_y', 'rotation_z',
        'scale_x', 'scale_y', 'scale_z')
    for to_ignore in attributes_to_ignore:
        del defaults[to_ignore]

    print(entity.children)

        # instance_attributes = e.__dict__
        # print('self.entity.name = ' + e.name)
        # for a in instance_attributes:
        #     value = instance_attributes.get(a)
        #     if not value == defaults.get(a):
        #         print('self.entity.' + str(a), ' = ', value)

# folders = list()

def load_prefab(module_name):
    folders = ('internal_prefabs.', '..prefabs.')
    prefab = load(folders, module_name)
    caller = inspect.currentframe().f_back.f_locals['self']
    # if hasattr(caller, 'name') and caller.name == 'editor':
    #     prefab.is_editor = True
    # if the caller is attached to an entity, parent the prefab to it.
    try: prefab.parent = caller.model
    except:
        try: prefab.parent = caller
        except: pass

    return prefab

def load_scene(module_name):
    scene.clear()
    importlib.reload(importlib.import_module('..scenes.' + module_name))
    print('loaded scene:', module_name)
    folders = ('..scenes.')
    return load(folders, module_name)

def load_script(module_name):
    folders = ('internal_scripts.', '..scripts.')
    return load(folders, module_name)



def load(folders, module_name):
    if inspect.isclass(module_name):
        class_instance = module_name()
        # print('added script:', class_instance)
        return class_instance

    # find the module
    module = None
    for f in folders:
        # print('mod:', f + module_name)
        try:
            module = importlib.import_module(f + module_name)
            break
        except:
            pass

    if not module:
        # print(module_name, 'not found')
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
