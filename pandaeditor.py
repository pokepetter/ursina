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
import application
import scene
import mouse
import window
import camera
import debug
import color

from internal_scripts import *
# from internal_scenes import *
from internal_prefabs import *





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
        if not e.is_editor and e.parent == scene.render and e is not scene_entity:
            print(e)
            e.parent = parent_entity
    save_prefab(scene_entity, name)
    # for e in scene.entities:
        # if e.parent = parent_entity


def save_prefab(target, folder='prefabs'):
    prefab_path = os.path.join(
        os.path.dirname(application.asset_folder),
        'scenes',
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
            if parent_str == 'render_2':
                parent_str = 'camera.render'
            if e.parent == target:
                parent_str = 'self'


            file.write(prefix + '.enabled = ' + str(e.enabled) + '\n'
                + prefix + '.is_editor = ' + str(e.is_editor) + '\n'
                + prefix + '.name = ' + '\'' + str(e.name) + '\'' + '\n'
                + prefix + '.parent = ' + parent_str + '\n')

            if e.model:
                file.write(prefix + '.model = ' + '\'' + os.path.basename(str(e.model))[:4] + '\'' + '\n')
            if e.color:
                file.write(prefix + '.color = ' + color_str + '\n')
            if e.texture:
                file.write(prefix + '.texture = ' + str(e.texture) + '\n')

            file.write(prefix + '.collision = ' + str(e.collision) + '\n')
            if e.collider:
                file.write(prefix + '.collider = ' + str(e.collider) + '\n')

            file.write(
                prefix + '.origin = (' + str(e.origin[0]) + ', ' +  str(e.origin[1]) + ', ' +  str(e.origin[2]) + ')' + '\n'
                + prefix + '.position = (' + str(e.position[0]) + ', ' +  str(e.position[1]) + ', ' +  str(e.position[2]) + ')' + '\n'
                + prefix + '.rotation = (' + str(e.rotation[0]) + ', ' +  str(e.rotation[1]) + ', ' +  str(e.rotation[2]) + ')' + '\n'
                + prefix + '.scale = (' + str(e.scale[0]) + ', ' +  str(e.scale[1]) + ', ' +  str(e.scale[2]) + ')' + '\n'
                )

            for s in e.scripts:
                if e is target:
                    script_prefix = prefix + '.' + str(s.__class__.__name__).lower()
                else:
                    script_prefix = prefix + '_' + str(s.__class__.__name__).lower()

                file.write(script_prefix + ' = ' + prefix[8:] + '.add_script(\'' + s.__class__.__name__ + '\')\n')
                scripts_vars = [item for item in dir(s) if not item.startswith('_')]
                for var in scripts_vars:
                    varvalue = getattr(s, var)

                    if not varvalue:
                        continue

                    if varvalue.__class__ == Entity:
                        if varvalue == target:
                            varvalue = 'self'
                        else:
                            varvalue = str(varvalue.name) + '_' + str(varvalue.get_key())

                    file.write(script_prefix + '.' + var + ' = ' + str(varvalue) + '\n')


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
    # scene.clear()
    omn = module_name
    module_name += '.py'
    module_names = (os.path.join(os.path.dirname(__file__), module_name),
                    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scenes', module_name))

    for module_name in module_names:
        try:
            module = importlib.machinery.SourceFileLoader(omn, module_name).load_module()
            class_names = inspect.getmembers(sys.modules[omn], inspect.isclass)
            for cn in class_names:
                if cn[1].__module__ == module.__name__:
                    class_name = cn[0]
            class_ = getattr(module, class_name)
            class_instance = class_()
            class_instance.parent = scene
            destroy(scene.entity)
            scene.entity = class_instance
            print('found scene!')
            # print(scene.entities)
            return class_instance
            break
        except Exception as e:
            print(e)

    print("couldn't find scene:", omn)

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
