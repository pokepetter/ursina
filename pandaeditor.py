from direct.showbase.ShowBase import ShowBase
from panda3d.core import Lens
from panda3d.core import PerspectiveLens
from panda3d.core import OrthographicLens
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.task.Task import Task
from panda3d.core import NodePath
from panda3d.core import PandaNode
from panda3d.core import Vec3
from panda3d.core import Point3
from panda3d.bullet import BulletWorld


import sys
import math
import inspect
import importlib

import mouse
import collision
import scene
import camera
import debug
import color
from entity import Entity

from scripts import *
from scenes import *
from prefabs import *

from panda3d.core import loadPrcFileData




screen_size = (1280, 720)


def distance(a, b):
    return math.sqrt(sum( (a - b)**2 for a, b in zip(a, b)))

def load_prefab(module_name):
    # try:
    #     importlib.reload(importlib.import_module('prefabs.' + module_name))
    # except:
    #     pass
    prefab = load_script('prefabs.' + module_name)
    caller = inspect.currentframe().f_back.f_locals['self']
    scene.entities.append(prefab)

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
    try: entity.model.removeNode()
    except: pass
    try: entity.removeNode()
    except: pass
    del entity
