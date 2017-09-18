import sys
import inspect
import importlib
from panda3d.core import PandaNode
from panda3d.core import NodePath
from panda3d.core import Vec3
from panda3d.core import SamplerState
from panda3d.core import TransparencyAttrib
from collider import Collider
from scripts import *
import uuid
import color
import scene
from os import path
from panda3d.core import Filename


class Entity(NodePath):

    def __init__(self):
        super().__init__('empty')
        self.enabled = True
        self.visible = True
        self.is_editor = False
        # self.prefab_name = None
        self.name = 'entity'
        self.parent = scene.render
        self.children = list()
        self.scripts = list()
        self.model = None
        self.texture = None
        self.color = color.gray
        self.collision = False
        self.collider = None
        self.hovered = False

        self.origin = (0,0,0)
        self.position = Vec3(0,0,0)
        self.x, self.y, self.z = 0, 0, 0

        self.forward, self.back = Vec3(0,0,1), Vec3(0,0,-1)
        self.right, self.left = Vec3(1,0,0), Vec3(-1,0,0)
        self.up, self.down = Vec3(0,1,0), Vec3(0,-1,0)

        self.rotation = (0,0,0)
        self.rotation_x, self.rotation_y, self.rotation_z = 0, 0, 0

        self.setting_scale = 0
        self.scale = Vec3(1,1,1)
        self.scale_x, self.scale_y, self.scale_z = 1, 1, 1

        scene.entities.append(self)


    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except:
            pass
        if name == 'enabled':
            try:
                # try calling on_enable() on classes inheriting from Entity
                if value == 1:
                    self.on_enable()
                else:
                    self.on_disable()
            except:
                self.visible = value

        if name == 'visible':
            try:
                if value == False:
                    self.hide()
                    self.collider.stash()
                    # self.collider.node_path.setTangible(0)
                else:
                    self.show()
                    self.collider.unstash()
                    # self.collider.node_path.setTangible(1)
            except:
                pass # no model

        if name == 'parent' and value != None:
            try:
                self.reparentTo(value)
            except:
                try:
                    self.reparentTo(value.model)
                except: pass
        if name == 'model':
            if value == None:
                return None

            # self.model = None

            try:
                combined_path = (path.join(
                    path.dirname(__file__),
                    'internal_models/')
                    + value + '.egg')
                combined_path = Filename.fromOsSpecific(combined_path)
                # print('trying to load:', combined_path)
                self.model = loader.loadModel(combined_path)
            except:
                pass
                # try:
                #     self.model = loader.loadModel('..internal_models/' + value + '.egg')
                # except:
                #     pass

            if self.model:
                self.model.reparentTo(self)
                self.model.setColorScaleOff()
                self.model.setTransparency(TransparencyAttrib.MAlpha)
            else:
                print('no model with name:', combined_path)

        if name == 'color':
            if self.model:
                self.model.setColorScale(value)
        if name == 'texture':
            if self.model:
                try:
                    texture = loader.loadTexture(Filename.fromOsSpecific(value))
                except:
                    try:
                        texture = loader.loadTexture(
                            Filename.fromOsSpecific(
                            (path.join(
                                pathf.dirname(path.dirname(__file__)),
                                'textures/') + value)))
                    except:
                        pass
                object.__setattr__(self, name, texture)
                # texture.setMagfilter(SamplerState.FT_nearest)
                # texture.setMinfilter(SamplerState.FT_nearest)
                self.model.setTexture(texture, 1)

        if name == 'position':
            # automatically add position instead of extending the tuple
            # print(value)
            new_value = Vec3()

            if len(value) % 2 == 0:
                for i in range(0, len(value), 2):
                    new_value.addX(value[i])
                    new_value.addY(value[i+1])
                new_value.addZ(self.getY())

            if len(value) % 3 == 0:
                for i in range(0, len(value), 3):
                    new_value.addX(value[i])
                    new_value.addY(value[i+1])
                    new_value.addZ(value[i+2])
            try:
                self.setPos(Vec3(new_value[0], new_value[2], new_value[1]))
                object.__setattr__(self, name, new_value)
                object.__setattr__(self, 'x', new_value[0])
                object.__setattr__(self, 'y', new_value[1])
                object.__setattr__(self, 'z', new_value[2])
            except:
                pass #cant set position


        if name == 'x': self.position = (value, self.position[1], self.position[2])
        if name == 'y': self.position = (self.position[0], value, self.position[2])
        if name == 'z': self.position = (self.position[0], self.position[1], value)

        if name == 'origin' and self.model:
            new_value = Vec3()

            if len(value) % 2 == 0:
                for i in range(0, len(value), 2):
                    new_value.addX(value[i])
                    new_value.addY(value[i+1])
                new_value.addZ(self.model.getY())

            if len(value) % 3 == 0:
                for i in range(0, len(value), 3):
                    new_value.addX(value[i])
                    new_value.addY(value[i+1])
                    new_value.addZ(value[i+2])

            self.model.setPos(-new_value[0],
                                -new_value[2],
                                -new_value[1])
            object.__setattr__(self, name, new_value)

        if name == 'rotation':
            try:
                # convert value from hpr to axis
                value = (value[2] , value[0], value[1])
                self.setHpr(value)
                object.__setattr__(self, name, (value[1] , value[2], value[0]))
                object.__setattr__(self, 'rotation_x', value[0])
                object.__setattr__(self, 'rotation_y', value[1])
                object.__setattr__(self, 'rotation_z', value[2])
            except:
                pass

        if name == 'rotation_x': self.rotation = (value, self.rotation[1], self.rotation[2])
        if name == 'rotation_y': self.rotation = (self.rotation[0], value, self.rotation[2])
        if name == 'rotation_z': self.rotation = (self.rotation[0], self.rotation[1], value)

        if name == 'scale':
            new_value = Vec3()

            if len(value) % 2 == 0:
                for i in range(0, len(value), 2):
                    new_value.addX(value[i])
                    new_value.addY(value[i+1])
                new_value.addZ(self.getSy())

            if len(value) % 3 == 0:
                for i in range(0, len(value), 3):
                    new_value.addX(value[i])
                    new_value.addY(value[i+1])
                    new_value.addZ(value[i+2])
            try:
                self.setScale(Vec3(new_value[0], new_value[2], new_value[1]))
                object.__setattr__(self, name, new_value)
                object.__setattr__(self, 'scale_x', new_value[0])
                object.__setattr__(self, 'scale_y', new_value[1])
                object.__setattr__(self, 'scale_z', new_value[2])
            except:
                pass


        if name == 'scale_x': self.scale = (value, self.scale[1], self.scale[2])
        if name == 'scale_y': self.scale = (self.scale[0], value, self.scale[2])
        if name == 'scale_z': self.scale = (self.scale[0], self.scale[1], value)


        if name == 'collider' and value != None:
            collider = Collider()
            collider.entity = self
            collider.make_collider()
            object.__setattr__(self, name, collider)

        if name == 'editor_collider' and value != None:
            editor_collider = Collider()
            editor_collider.entity = self
            editor_collider.make_collider()
            object.__setattr__(self, name, editor_collider)


    def __getattr__(self, attrname):
        if attrname == 'global_position':
            global_position = self.getPos(scene.render)
            global_position = (global_position[0], global_position[2], global_position[1])
            return global_position
        else:
            try:
                return self.attrname
            except:
                pass
                # raise AttributeError()

        if attrname == 'chi':
            print('getting children')
            all_children = super().children
            new_children = list()
            for child in all_children:
                if not child.endswith('.egg'):
                    new_children.append(child)

            return all_children
            # for c in self.getChildren():
            #     print(c.__class__)
            #     if c.__class__.__name__ == 'Entity':


        if attrname == 'forward':
            return scene.render.getRelativeVector(self, (0,0,1))
        if attrname == 'back':
            return scene.render.getRelativeVector(self, (0,0,-1))
        if attrname == 'right':
            return scene.render.getRelativeVector(self, (1,0,0))
        if attrname == 'left':
            return scene.render.getRelativeVector(self, (-1,0,0))
        if attrname == 'up':
            return scene.render.getRelativeVector(self, (0,1,0))
        if attrname == 'down':
            return scene.render.getRelativeVector(self, (0,-1,0))


    def add_script(self, module_name):
        if inspect.isclass(module_name):
            class_instance = module_name()
            try:
                class_instance.entity = self
            except:
                print(class_instance, 'has no target variable')
            self.scripts.append(class_instance)
            return class_instance

        module_names = (module_name,
                        'internal_scripts.' + module_name,
                        '..scripts.' + module_name)
                        # 'scenes.' + module_name,
                        # 'prefabs.' + module_name)
        for module_name in module_names:
            try:
                module = importlib.import_module(module_name)
                class_names = inspect.getmembers(sys.modules[module_name], inspect.isclass)
                for cn in class_names:
                    if cn[1].__module__ == module.__name__:
                        class_name = cn[0]

                class_ = getattr(module, class_name)
                class_instance = class_()
                try:
                    class_instance.entity = self
                except:
                    print(class_instance, 'has no target variable')

                self.scripts.append(class_instance)
                return class_instance
                break
            except:
                pass

        # print("couldn't find script:", module_name)

    def look_at(self, target):
        super().look_at(target)
        self.setH(self.getH()-180)
        self.setP(self.getP() * -1)


    def get_script(self, type):
        pass


    def has_ancestor(self, ancestor):
        p = self
        for i in range(100):
            if p.parent:
                if p.parent == ancestor:
                    return True
                    break
                p = p.parent



    # def get_children(self):
        # for child in self.getChildren():
        #     print(child.name)
        # for
