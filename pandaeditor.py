from direct.showbase.ShowBase import ShowBase
from panda3d.core import Lens
from panda3d.core import PerspectiveLens
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.task.Task import Task
# from direct.gui.OnscreenText import OnscreenText
from panda3d.core import NodePath
from panda3d.core import PandaNode
from panda3d.core import Vec3
from panda3d.core import Point3

import sys
import math

import mouse
import collision
import camera
import debug
import color
from gameobject import Gameobject
from button import Button

# from panda3d.core import ClockObject
from panda3d.core import loadPrcFileData
# from direct.gui.DirectGui import *
# from direct.gui import DirectGuiGlobals
# from panda3d.core import CardMaker

screen_size = (960, 540)

def distance(a, b):
    print(math.sqrt(sum( (a - b)**2 for a, b in zip(a, b))))
    return math.sqrt(sum( (a - b)**2 for a, b in zip(a, b)))
