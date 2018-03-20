import sys
import inspect
import importlib
import random
from panda3d.core import PandaNode
from panda3d.core import NodePath
from panda3d.core import ModelNode
from panda3d.core import Vec3
from panda3d.core import Point3
from panda3d.core import SamplerState
from panda3d.core import TransparencyAttrib
from panda3d.core import Texture
from pandaeditor import application
from pandaeditor.collider import Collider
import uuid
from os import path
from panda3d.core import Filename
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from undo import undoable
from direct.showbase import Loader
from pandaeditor.pandamath import lerp
from pandaeditor import easing_types
from pandaeditor.easing_types import *

from pandaeditor import color
from pandaeditor import scene


class Entity(NodePath):

    def __init__(self, name='entity', **kwargs):
        super().__init__(name)
        self.name = name
        self.enabled = True
        self.is_editor = False
        try:
            self.parent = scene
        except:
            print('scene not yet initialized')
        scene.has_changes = True
        self.model = None
        self.color = color.white
        self.texture = None
        self.collision = False
        # self.collider = None
        self.editor_collider = None
        self.scripts = list()
        self.prefab_name = None
        self.hovered = False

        self.origin = Vec3(0,0,0)
        self.position = Vec3(0,0,0)
        self.x, self.y, self.z = 0, 0, 0

        self.rotation = Vec3(0,0,0)
        self.rotation_x, self.rotation_y, self.rotation_z = 0, 0, 0

        self.scale = Vec3(1,1,1)
        self.scale_x, self.scale_y, self.scale_z = 1, 1, 1

        scene.entities.append(self)

        for key, value in kwargs.items():
            setattr(self, key, value)


    def __setattr__(self, name, value):

        if name == 'enabled':
            try:
                # try calling on_enable() on classes inheriting from Entity
                if value == True:
                    self.on_enable()
                else:
                    self.on_disable()
            except:
                pass

            if value == True:
                if not self.is_singleton():
                    self.unstash()
            else:
                if not self.is_singleton():
                    self.stash()

        if name == 'parent':
            if value is None:
                try:
                    self.reparentTo(scene.editor.trash)
                except:
                    print('no trash node')
            else:
                try:
                    self.reparentTo(value)
                except:
                    print('invalid parent:', value)

        if name == 'model':
            if value is None:
                if hasattr(self, 'model') and self.model != None:
                    print('romve model')
                    self.model.removeNode()
                    print('romved node')
                return None

            if isinstance(value, str):
                try:
                    object.__setattr__(self, name, loader.loadModel(value))
                # print('loaded model:', value)
                except:
                    pass
                    return

            if hasattr(self, 'model') and self.model:
                self.model.reparentTo(self)
                self.model.setColorScaleOff()
                self.model.setTransparency(TransparencyAttrib.MAlpha)
                return
            else:
                print('missing model:', value)

        if name == 'color' and value is not None:
            if hasattr(self, 'model') and self.model:
                self.model.setColorScale(value)
                object.__setattr__(self, name, value)

        if name == 'texture':
            if not hasattr(self, 'model') or hasattr(self, 'model') and not self.model:
                return

            if value.__class__ is Texture:
                texture = value
            elif isinstance(value, str):
                try:
                    texture = loader.loadTexture(value + '.png')
                except:
                    try:
                        texture = loader.loadTexture(value + '.jpg')
                    except:
                        print('no texture:', value + '.png or', value + '.jpg')
                        return None

            try:
                object.__setattr__(self, name, texture)
                texture.setMagfilter(SamplerState.FT_nearest)
                texture.setMinfilter(SamplerState.FT_nearest)
                self.model.setTexture(texture, 1)
                # print('set texture:', value)
            except:
                pass
                print('no texture:', value)

            if value == None:
                self.model.set_texture_off(True)


        if name == 'position':
            # automatically add position instead of extending the tuple
            new_value = Vec3()

            if len(value) % 2 == 0:
                for i in range(0, len(value), 2):
                    new_value.add_x(value[i])
                    new_value.add_y(value[i+1])
                new_value.add_z(self.getY())

            if len(value) % 3 == 0:
                for i in range(0, len(value), 3):
                    new_value.add_x(value[i])
                    new_value.add_y(value[i+1])
                    new_value.add_z(value[i+2])

            try:
                self.setPos(new_value[0], new_value[2], new_value[1])
            except:
                pass    # can't set position

        if name == 'x': self.setX(value)
        if name == 'y': self.setZ(value)
        if name == 'z': self.setY(value)

        if name == 'origin' and hasattr(self, 'model') and self.model:
            new_value = Vec3()

            if len(value) % 2 == 0:
                for i in range(0, len(value), 2):
                    new_value.add_x(value[i])
                    new_value.add_y(value[i+1])
                new_value.add_z(self.model.getY())

            if len(value) % 3 == 0:
                for i in range(0, len(value), 3):
                    new_value.add_x(value[i])
                    new_value.add_y(value[i+1])
                    new_value.add_z(value[i+2])

            self.model.setPos(-new_value[0], -new_value[2], -new_value[1])
            object.__setattr__(self, name, new_value)
            return

        if name == 'rotation':
            new_value = Vec3()

            if len(value) % 2 == 0:
                for i in range(0, len(value), 2):
                    new_value.add_x(value[i])
                    new_value.add_y(value[i+1])
                new_value.add_z(self.getR())

            if len(value) % 3 == 0:
                for i in range(0, len(value), 3):
                    new_value.add_x(value[i])
                    new_value.add_y(value[i+1])
                    new_value.add_z(value[i+2])

            self.setHpr(Vec3(-new_value[1], -new_value[0], new_value[2]))


        if name == 'rotation_x': self.setP(-value)
        if name == 'rotation_y': self.setH(-value)
        if name == 'rotation_z': self.setR(value)

        if name == 'scale':
            new_value = Vec3()

            if len(value) % 2 == 0:
                for i in range(0, len(value), 2):
                    new_value.add_x(value[i])
                    new_value.add_y(value[i+1])
                new_value.add_z(self.getSy())

            if len(value) % 3 == 0:
                for i in range(0, len(value), 3):
                    new_value.add_x(value[i])
                    new_value.add_y(value[i+1])
                    new_value.add_z(value[i+2])
            self.set_scale(new_value[0], new_value[2], new_value[1])


        if name == 'scale_x': self.set_scale(value, self.scale_z, self.scale_y)
        if name == 'scale_y': self.set_scale(self.scale_x, self.scale_z, value)
        if name == 'scale_z': self.set_scale(self.scale_x, value, self.scale_y)


        if name == 'collider':
            if value == None and self.collider:
                print('ccccc', type(self.collider))
                # if self.collider:
                from pandaeditor.pandastuff import destroy
                destroy(self.collider)
                print('__________', self.collider)
                if type(self.collider) is Entity:
                    self.collider.remove_node()
                del(self.collider)
                object.__setattr__(self, name, None)
                return
                # print(self.collider)
            elif value == 'box' and hasattr(self, 'model'):
                collider = Collider()
                collider.entity = self
                collider.make_collider()
                object.__setattr__(self, name, collider)
                return

        if name == 'editor_collider':
            if value is not None:
                editor_collider = Collider()
                editor_collider.entity = self
                editor_collider.make_collider()
                object.__setattr__(self, name, editor_collider)
            elif hasattr(self, 'editor_collider') and self.editor_collider:
                print('destroy collider')

        if name == 'render_queue':
            if self.model:
                self.model.setBin("fixed", value)
            # model.setDepthTest(False)
            # model.setDepthWrite(False)

        try:
            super().__setattr__(name, value)
        except:
            pass
            # print('failed to sett attribiute:', name)


    @property
    def world_position(self):
        world_position = self.getPos(render)
        world_position = Vec3(world_position[0], world_position[2], world_position[1])
        return world_position

    @world_position.setter
    def world_position(self, value):
        self.setPos(value, render)

    @property
    def world_x(self):
        return self.getX(render)
    @property
    def world_y(self):
        return self.getZ(render)
    @property
    def world_z(self):
        return self.getY(render)

    @world_x.setter
    def world_x(self, value):
        self.setX(render, value)
    @world_y.setter
    def world_y(self, value):
        self.setZ(render, value)
    @world_z.setter
    def world_z(self, value):
        self.setY(render, value)

    @property
    def position(self):
        return Vec3(self.getX(), self.getZ(), self.getY())
    @property
    def x(self):
        return self.getX()
    @property
    def y(self):
        return self.getZ()
    @property
    def z(self):
        return self.getY()

    @property
    def rotation(self):
        return(-self.getP(), -self.getH(), self.getR())
    @property
    def rotation_x(self):
        return -self.getP()
    @property
    def rotation_y(self):
        return -self.getH()
    @property
    def rotation_z(self):
        return self.getR()

    @property
    def scale(self):
        scale = self.getScale()
        return Vec3(scale[0], scale[2], scale[1])
    @property
    def scale_x(self):
        return self.getScale()[0]
    @property
    def scale_y(self):
        return self.getScale()[2]
    @property
    def scale_z(self):
        return self.getScale()[1]

    @property
    def forward(self):
        vec =  render.getRelativeVector(self, (0, 1, 0))
        return Vec3(vec[0], vec[2], vec[1])
    @property
    def back(self):
        return -self.forward
    @property
    def right(self):
        vec =  render.getRelativeVector(self, (1, 0, 0))
        return Vec3(vec[0], vec[2], vec[1])
    @property
    def left(self):
        return -self.right
    @property
    def up(self):
        vec = render.getRelativeVector(self, (0, 0, 1))
        return Vec3(vec[0], vec[2], vec[1])
    @property
    def down(self):
        return -self.up



    def reparent_to(self, entity):
        self.wrtReparentTo(entity)
        # pos = self.getPos(entity)
        # self.position = (pos[0], pos[2], pos[1])
        # self.__setattr__('scale', self.getScale(entity))
        # print('parent:', self.parent.name, 'newpos:', self.position)

    def add_script(self, module_name):
        # instance given
        if isinstance(module_name, object) and type(module_name) is not str:
            print('type', type(self))
            module_name.entity = self
            self.scripts.append(module_name)
            # print('added script:', module_name)
            return module_name

        # class name given
        if inspect.isclass(module_name):
            class_instance = module_name()
            class_instance.entity = self
            self.scripts.append(class_instance)
            # print('added script:', module_name)
            return class_instance

        # module name given
        omn = module_name
        module_name += '.py'
        module_names = (path.join(path.dirname(__file__), module_name),
                        path.join(application.internal_script_folder , module_name),
                        path.join(application.script_folder, module_name))

        for module_name in module_names:
            try:
                module = importlib.machinery.SourceFileLoader(omn, module_name).load_module()
                class_names = inspect.getmembers(sys.modules[omn], inspect.isclass)
                for cn in class_names:
                    if cn[1].__module__ == module.__name__:
                        class_name = cn[0]

                class_ = getattr(module, class_name)
                class_instance = class_()
                class_instance.entity = self

                name = module.__name__.split('.')
                name = name[-1]
                setattr(self, name, class_instance)
                self.scripts.append(class_instance)
                # print('added script:', module_name)
                return class_instance
                break
            except Exception as e:
                if e is FileNotFoundError == False:
                    print(e)

        print("couldn't find script:", module_names)

    @undoable
    def remove_script(self, module_name):
        for s in self.scripts:
            if s.__module__ == module_name:
                self.temp_script = s
                self.scripts.remove(s)
                self.__setattr__(module_name, None)
                print('removed:', module_name)
        # undo
        yield 'remove' + module_name
        self.scripts.append(self.temp_script)
        self.__setattr__(module_name, self.temp_script)


    def look_at(self, target):
        if type(target) is Vec3:
            super().look_at(Vec3(target[0], target[2], target[1]))
            return
        super().look_at(target)


    def get_scripts_of_type(self, type):
        pass


    def has_ancestor(self, ancestor):
        p = self
        for i in range(100):
            if p.parent:
                if p.parent == ancestor:
                    return True
                    break
                p = p.parent

    @property
    def children(self):
        children_entities = list()
        for e in scene.entities:
            if e.parent == self:
                children_entities.append(e)


        return children_entities

#------------
# ANIMATIONS
#------------

    def move(self, value, duration=.1, delay=0, curve='linear'):
        s = Sequence()
        s.append(Wait(delay))
        s.append(self.posInterval(duration, Point3(value[0], value[2], value[1])))
        s.start()
        return s

    def move_x(self, value, duration=.1, delay=0, curve='linear', resolution=5):
        s = Sequence()
        s.append(Wait(delay))
        start_val = self.x
        for i in range(resolution+1):
            t = i / resolution
            t = t*t
            s.append(Wait(duration / resolution))
            s.append(Func(self.setX, lerp(start_val, value, t)))

        s.start()
        return s

    def move_y(self, value, duration=.1, delay=0, curve='linear', resolution=None):
        if hasattr(self, 'mover_y') and self.mover_y:
            self.mover_y.pause()
            # print('interrupt mover_y')
        self.mover_y = Sequence()
        self.mover_y.append(Wait(delay))
        start_val = self.y
        if not resolution:
            resolution = int(duration * 60)

        for i in range(resolution+1):
            t = i / resolution
            if hasattr(easing_types, curve):
                t = getattr(easing_types, curve)(t)
            else:
                t = getattr(easing_types, 'ease_in_expo')(t)
            self.mover_y.append(Wait(duration / resolution))
            self.mover_y.append(Func(self.setZ, lerp(start_val, value, t)))

        self.mover_y.start()
        return self.mover_y



    def move_z(self, value, duration=.1, delay=0, curve='linear'):
        s = Sequence()
        s.append(Wait(delay))
        s.append(self.posInterval(duration, Point3(self.x, value, self.y)))
        s.start()
        return s


    def animate_scale(self, value, duration=.1, delay=0, curve='linear'):
        s = Sequence()
        s.append(Wait(delay))
        s.append(self.scaleInterval(duration, Vec3(value[0], value[2], value[1])))
        s.start()
        return s

    def animate_scale_x(self, value, duration=.1, delay=0, curve='linear'):
        s = Sequence()
        s.append(Wait(delay))
        s.append(self.scaleInterval(duration, Vec3(value, self.scale_z, self.scale_y)))
        s.start()
        return s

    def animate_scale_y(self, value, duration=.1, delay=0, curve='linear'):
        s = Sequence()
        s.append(Wait(delay))
        s.append(self.scaleInterval(duration, Vec3(self.scale_x, self.scale_z, value)))
        s.start()
        return s

    def animate_scale_z(self, value, duration=.1, delay=0, curve='linear'):
        s = Sequence()
        s.append(Wait(delay))
        s.append(self.scaleInterval(duration, Vec3(self.scale_x, value, self.scale_y)))
        s.start()
        return s

    def shake(self, duration=.2, magnitude=1):
        s = Sequence()
        self.original_position = self.position
        for i in range(int(duration / .05)):
            s.append(self.posInterval(.05, Point3(
                self.x + (random.uniform(-.1, .1) * magnitude),
                self.z,
                self.y + (random.uniform(-.1, .1) * magnitude))
            ))
            s.append(self.posInterval(.05, Point3(
                self.original_position[0],
                self.original_position[2],
                self.original_position[1])
            ))
        s.start()


    # @property
    # def descendants(self):
    #     descendants = list()
    #     for e in scene.entities:
    #         if e.parent == self:
    #             children_entities.append(e)
    #
    #     # for c in super().children:
    #     #     if Entity in c.__class__.__subclasses__():
    #     #         # children_entities.append(c)
    #     #         print(c.__class__.__name__)
    #
    #     return children_entities
class ShakeTester(Entity):
    def __init__(self):
        super().__init__()
        self.move = 1
        self.move_y = 1
        self.frame = 0
        self.d = False

    def input(self, key):
        if key == '1':
            e.shake()

        if key == 'x':
            self.move = -self.move
            e.move_x(self.x + self.move)

        if key == 'y':
            self.move_y = -self.move_y
            e.move_y(self.y + self.move_y)

        if key == 'd':
            self.d = True
        if key == 'd up':
            self.d = False

        if key == 'space':
            e.move_y(e.y + 2.5, .7)
            invoke(self.fall, delay=.5)

    def fall(self):
        print('fall')
        e.move_y(0, duration=.5)

    def update(self, dt):
        self.frame += 1
        if self.frame >= 4:
            if self.d:
                e.move_x(self.x + 1, 1/60 * 4)
            self.frame = 0



if __name__ == '__main__':
    from pandaeditor import main
    from pandastuff import printvar, invoke

    app = main.PandaEditor()
    # e = Entity()
    # e.enabled = True
    # e.model = 'quad'
    # e.color = color.red
    # e.collider = 'box'
    # e.collider = None


    print(lerp(0, 10, .5))

    e = Entity(model='quad', color=color.red, collider='box')
    printvar(e.world_position)

    e.world_x = 1
    e.world_y = 1
    e.world_z = 1
    printvar(e.world_x)
    printvar(e.world_y)
    printvar(e.world_z)


    # e.model = None

    shake_tester = ShakeTester()
    app.run()
