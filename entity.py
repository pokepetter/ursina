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
from scenes import *
import color
import scene


class Entity(NodePath):

    def __init__(self):
        super().__init__('empty')
        self.enabled = True
        self.visible = True
        self.is_editor = False
        self.name = 'entity'
        self.parent = scene.render
        self.scripts = list()
        self.model = None
        self.texture = None
        self.color = color.gray
        self.collision = False
        self.collider = None
        self.hovered = False

        self.global_position = (0,0,0)
        self.position = (0,0,0)
        self.x, self.y, self.z = 0, 0, 0

        self.forward, self.back = (0,0,0), (0,0,0)
        self.right, self.left = (0,0,0), (0,0,0)
        self.up, self.down = (0,0,0), (0,0,0)

        self.rotation = (0,0,0)
        self.rotation_x, self.rotation_y, self.rotation_z = 0, 0, 0

        self.scale = (1,1,1)
        self.scale_x, self.scale_y, self.scale_z = 0, 0, 0


    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except:
            pass
        if name == 'visible':
            try:
                if value == False:
                    self.hide()
                else:
                    self.show()
            except:
                pass # no model

        if name == 'parent' and value != None:
            try: self.reparentTo(value)
            except:
                try: self.reparentTo(value.model)
                except: pass
        if name == 'model':
            try:
                self.model = loader.loadModel('models/' + value + '.egg')
                self.model.reparentTo(self)
                self.model.setColorScaleOff()
                self.model.setTransparency(TransparencyAttrib.MAlpha)
            except:
                pass
                # print('no model with name:', 'models/', value)
        if name == 'color':
            if self.model:
                self.model.setColorScale(value)
        if name == 'texture':
            if self.model:
                texture = loader.loadTexture(value)
                object.__setattr__(self, name, texture)
                # texture.setMagfilter(SamplerState.FT_nearest)
                # texture.setMinfilter(SamplerState.FT_nearest)
                self.model.setTexture(texture, 1)
        if name == 'global_position':
            self.setPos(Vec3(value[0], value[1], value[2]))
        if name == 'position':
            # automatically add position instead of extending the tuple

            new_value = Vec3()
            for i in range(0, len(value), 3):
                new_value.addX(value[i])
                new_value.addY(value[i+1])
                new_value.addZ(value[i+2])
            value = new_value
            self.setPos(new_value)
            object.__setattr__(self, name, (value[0], value[1], value[2]))

        if name == 'x': self.position = (value, self.position[1], self.position[2])
        if name == 'y': self.position = (self.position[0], value, self.position[2])
        if name == 'z': self.position = (self.position[0], self.position[1], value)

        if name == 'origin':
            self.model.setPos(-value[0] /2,
                                -value[1] /2,
                                -value[2] /2)

        if name == 'rotation':
            try:
                # convert value from hpr to axis
                value = (value[2] , value[0], value[1])
                self.setHpr(value)

                forward = scene.render.getRelativeVector(self, (0,1,0))
                self.forward = (forward[0], forward[1], forward[2])
                self.back = (-forward[0], -forward[1], -forward[2])

                right = scene.render.getRelativeVector(self, (1,0,0))
                self.right = (right[0], right[1], right[2])
                self.left = (-right[0], -right[1], -right[2])

                up = scene.render.getRelativeVector(self, (0,0,1))
                self.up = (up[0], up[1], up[2])
                self.down = (-up[0], -up[1], -up[2])
            except:
                pass

        if name == 'rotation_x': self.rotation = (value, self.rotation[1], self.rotation[2])
        if name == 'rotation_y': self.rotation = (self.rotation[0], value, self.rotation[2])
        if name == 'rotation_z': self.rotation = (self.rotation[0], self.rotation[1], value)

        if name == 'scale':
            if self.model:
                self.setScale(value[0], value[1], value[2])
        #         self.model.setScale(self.parent, value[0], value[1], value[2])

        if name == 'collider':
            # if self.collider:
            #     self.collider.remove()

            collider = Collider()
            collider.parent = self
            collider.shape = value
            collider.position = (0,0,0)
            collider.rotation = (0,0,0)
            collider.scale = (1,1,1)
            object.__setattr__(self, name, collider)

            # self.collider = self.attachNewNode(collider)
            if scene.world:
                scene.world.attachRigidBody(collider)

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
                        'scripts.' + module_name,
                        'scenes.' + module_name,
                        'prefabs.' + module_name)
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
                # print('added script:', class_instance)
                return class_instance
                break
            except:
                pass

        # print("couldn't find script:", module_name)


    def get_script(self, type):
        pass

    # def get_children(self):
        # for child in self.getChildren():
        #     print(child.name)
        # for


    def destroy(self):
        pass

        parent.entities.remove(self)
        # nodePath.detachNode().
