import sys
import inspect
import importlib
from panda3d.core import PandaNode
from panda3d.core import NodePath
from panda3d.core import Vec3
from panda3d.core import SamplerState
from panda3d.core import TransparencyAttrib
from scripts import *
from scenes import *
import color
import scene


class Entity(object):

    def __init__(self):
        self.node_path = NodePath('empty')
        self.enabled = True
        self.name = 'entity'
        self.parent = None
        self.scripts = list()
        self.model = None
        self.color = color.gray
        self.collision = False
        self.collider = None
        self.hovered = False

        self.global_position = (0,0,0)
        self.position = (0,0,0)
        self.x, self.y, self.z = 0, 0, 0

        self.rotation = (0,0,0)
        self.rotation_x, self.rotation_y, self.rotation_z = 0, 0, 0

        self.scale = (1,1,1)
        self.scale_x, self.scale_y, self.scale_z = 0, 0, 0

        self.forward, self.back = (0,0,0), (0,0,0)
        self.right, self.left = (0,0,0), (0,0,0)
        self.up, self.down = (0,0,0), (0,0,0)


    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'enabled':
            try:
                if value == False:
                    self.model.hide()
                else:
                    self.model.show()
            except:
                pass # no model
            for child in self.node_path.getChildren():
                child.enabled = value
        if name == 'parent' and value != None:
            try: self.node_path.reparentTo(value)
            except:
                try: self.node_path.reparentTo(value.model)
                except: pass
        if name == 'model':
            if self.model:
                self.model.reparentTo(self.node_path)
                self.model.setColorScaleOff()
                self.model.setTransparency(TransparencyAttrib.MAlpha)
        if name == 'color':
            if self.model:
                self.model.setColorScale(value)
        if name == 'texture':
            if self.model:
                texture = loader.loadTexture(value)
                # texture.setMagfilter(SamplerState.FT_nearest)
                # texture.setMinfilter(SamplerState.FT_nearest)
                self.model.setTexture(texture, 1)
        if name == 'global_position':
            self.node_path.setPos(Vec3(value[0], value[1], value[2]))
        if name == 'position':
            # automatically add position instead of extending the tuple
            if len(value) % 3 == 0:
                new_value = Vec3()
                for i in range(0, len(value), 3):
                    new_value.addX(value[i])
                    new_value.addY(value[i+1])
                    new_value.addZ(value[i+2])
                value = new_value
                self.node_path.setPos(Vec3(value[0], value[1], value[2]))

        if name == 'x': self.position = (value, self.position[1], self.position[2])
        if name == 'y': self.position = (self.position[0], value, self.position[2])
        if name == 'z': self.position = (self.position[0], self.position[1], value)

        if name == 'origin':
            self.model.setPos(-value[0] /2,
                                -value[1] /2,
                                -value[2] /2)

        if name == 'scale':
            if self.model:
                self.node_path.setScale(value[0], value[1], value[2])
        #         self.model.setScale(self.parent, value[0], value[1], value[2])

        if name == 'collision':
            if value == False: self.collider = None
            if value == True and self.collider == None:
                try:
                    min, max = self.model.getTightBounds()
                    dimensions = max - min
                except:
                    dimensions = (1,1,1)

                collider_scale = self.model.getScale(scene.render)

                self.collider = ((0,0,0),
                                (0,0,0),
                                (dimensions[0] * collider_scale[0],
                                dimensions[1] * collider_scale[1],
                                dimensions[2] * collider_scale[2]))


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
                print('added script:', class_instance)
                return class_instance
                break
            except:
                pass

        print("couldn't find script:", module_name)


    def get_script(self, type):
        pass

    # def get_children(self):
        # for child in self.node_path.getChildren():
        #     print(child.name)
        # for


    def destroy(self):
        pass

        parent.entities.remove(self)
        # nodePath.detachNode().
