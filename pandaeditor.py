from direct.showbase.ShowBase import ShowBase
from panda3d.core import Lens
from panda3d.core import PerspectiveLens
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.task.Task import Task
from panda3d.core import NodePath
from panda3d.core import PandaNode
from panda3d.core import Vec3
from panda3d.core import Point3

import sys
import math
import inspect
import importlib

import mouse
import collision
import camera
import debug
import color
from entity import Entity
# from button import Button
# from ui import *

from scripts import *
from scenes import *

from panda3d.core import loadPrcFileData


screen_size = (960, 540)
entities = []
ui = None

def distance(a, b):
    return math.sqrt(sum( (a - b)**2 for a, b in zip(a, b)))

#
# def load_script(module_name):
#     if inspect.isclass(module_name):
#         class_instance = module_name()
#         return class_instance
#
#     module_names = (module_name, 'scripts.' + module_name, 'scenes.' + module_name)
#     for module_name in module_names:
#         try:
#             module = importlib.import_module(module_name, package=None)
#             class_names = inspect.getmembers(sys.modules[module_name], inspect.isclass)
#             for class_info in class_names:
#                 class_ = getattr(module, class_info[0])
#                 class_instance = class_()
#                 return class_instance
#         except:
#             pass
#     print("couldn't find script:", module_name)
