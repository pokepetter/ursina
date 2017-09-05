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


import sys
import math
import random
import inspect
import importlib

from entity import Entity
import scene
import mouse
import camera
import debug
import color

from scripts import *
from scenes import *
from prefabs import *

from panda3d.core import loadPrcFileData


editor = None
screen_size = (1920 * .6, 1080 * .6)


def distance(a, b):
    return math.sqrt(sum( (a - b)**2 for a, b in zip(a, b)))

def save_prefab(self, name):
    if len(self.entities) > 0:
        default_entity = Entity()
        defaults = default_entity.__dict__
        destroy(default_entity)
        attributes_to_ignore = (
            'x', 'y', 'z',
            'rotation_x', 'rotation_y', 'rotation_z',
            'scale_x', 'scale_y', 'scale_z')
        for to_ignore in attributes_to_ignore:
            del defaults[to_ignore]

        print('saving')
        for e in scene.entities:
            if not e.is_editor:
                instance_attributes = e.__dict__
                print('self.entity.name = ' + e.name)
                for a in instance_attributes:
                    value = instance_attributes.get(a)
                    if not value == defaults.get(a):
                        print('self.entity.' + str(a), ' = ', value)

def load_prefab(module_name):
    # try:
    #     importlib.reload(importlib.import_module('prefabs.' + module_name))
    # except:
    #     pass
    prefab = load_script('prefabs.' + module_name)
    caller = inspect.currentframe().f_back.f_locals['self']

    if hasattr(caller, 'name') and caller.name == 'editor':
        prefab.is_editor = True

    # if the caller is attached to an entity, parent the prefab to it.
    try: prefab.parent = caller.model
    except:
        try: prefab.parent = caller
        except: pass

    return prefab

def load_scene(module_name):
    scene.clear()
    importlib.reload(importlib.import_module('scenes.' + module_name))
    print('loaded scene:', module_name)
    return load_script('scenes.' + module_name)


def load_script(module_name):
    if inspect.isclass(module_name):
        class_instance = module_name()
        # print('added script:', class_instance)
        return class_instance
    # try:
    module = importlib.import_module(module_name)
    class_names = inspect.getmembers(sys.modules[module_name], inspect.isclass)
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
