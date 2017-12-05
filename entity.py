import sys
import inspect
import importlib
from panda3d.core import PandaNode
from panda3d.core import NodePath
from panda3d.core import ModelNode
from panda3d.core import Vec3
from panda3d.core import SamplerState
from panda3d.core import TransparencyAttrib
import application
from collider import Collider
from scripts import *
import uuid
import color
import scene
from os import path
from panda3d.core import Filename
from undo import undoable


class Entity(NodePath):

    def __init__(self):
        super().__init__('empty')
        self.enabled = True
        self.is_editor = False
        self.name = 'entity'
        self.parent = scene.entity
        self.model = None
        self.color = color.white
        self.texture = None
        self.collision = False
        self.collider = None
        self.editor_collider = None
        self.scripts = list()
        self.prefab_name = None
        self.hovered = False

        self.origin = Vec3(0,0,0)
        self.position = Vec3(0,0,0)
        self.x, self.y, self.z = 0, 0, 0

        # self.forward, self.back = Vec3(0,0,1), Vec3(0,0,-1)
        # self.right, self.left = Vec3(1,0,0), Vec3(-1,0,0)
        # self.up, self.down = Vec3(0,1,0), Vec3(0,-1,0)

        self.rotation = Vec3(0,0,0)
        self.rotation_x, self.rotation_y, self.rotation_z = 0, 0, 0

        self.scale = Vec3(1,1,1)
        self.scale_x, self.scale_y, self.scale_z = 1, 1, 1

        scene.entities.append(self)


    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except:
            pass
            # print('failed to sett attribiute:', name)

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
                self.stash()

        if name == 'parent' and value is not None:
            self.reparentTo(value)

        if name == 'model':
            if value is None:
                return None

            try:
                self.model = loader.loadModel(Filename.fromOsSpecific(path.join(
                        application.internal_model_folder, value + '.egg')))
                # print('loaded primitive')
            except:
                try:
                    self.model = loader.loadModel(Filename.fromOsSpecific(path.join(
                            application.model_folder, value + '.egg')))
                except:
                    pass

            if self.model:
                self.model.reparentTo(self)
                self.model.setColorScaleOff()
                self.model.setTransparency(TransparencyAttrib.MAlpha)
            else:
                print('no model with name:', combined_path)

        if name == 'color' and value is not None:
            if self.model:
                self.model.setColorScale(value)
                object.__setattr__(self, name, value)

        if name == 'texture':
            if not self.model:
                return

            try:
                texture = loader.loadTexture(
                    application.compressed_texture_folder + value + '.jpg'
                )
            except:
                try:
                    texture = loader.loadTexture(
                        application.compressed_texture_folder + value + '.png'
                    )
                except:
                    try:
                        texture = loader.loadTexture(Filename.fromOsSpecific(value))
                    except:
                        try:
                            texture = loader.loadTexture(
                                application.texture_folder + value
                            )
                        except:
                            try:
                                texture = loader.loadTexture(
                                    application.internal_texture_folder + value + '.png')
                            except:
                                pass

                if texture:
                    object.__setattr__(self, name, texture)
                    texture.setMagfilter(SamplerState.FT_nearest)
                    texture.setMinfilter(SamplerState.FT_nearest)
                    self.model.setTexture(texture, 1)
                # else:
                #     print('failed to load texture:', value)

        if name == 'position':
            # automatically add position instead of extending the tuple
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
                pass    # can't set position

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

            self.model.setPos(-new_value[0], -new_value[2], -new_value[1])
            object.__setattr__(self, name, new_value)

        if name == 'rotation':
            try:
                self.setHpr(Vec3(-value[1], -value[0], value[2]))
            except:
                pass

        if name == 'rotation_x': self.setP(-value)
        if name == 'rotation_y': self.setH(-value)
        if name == 'rotation_z': self.setR(value)

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


        if name == 'collider' and value is not None:
            collider = Collider()
            collider.entity = self
            collider.make_collider()
            object.__setattr__(self, name, collider)

        if name == 'editor_collider' and value is not None:
            editor_collider = Collider()
            editor_collider.entity = self
            editor_collider.make_collider()
            object.__setattr__(self, name, editor_collider)


    def __getattr__(self, attrname):
        if attrname == 'global_position':
            global_position = self.getPos(scene.render)
            global_position = (global_position[0], global_position[2], global_position[1])
            return global_position

        if attrname == 'rotation':
            return(-self.getP(), -self.getH(), self.getR())
        if attrname == 'rotation_x':
            return -self.getP()
        if attrname == 'rotation_y':
            return -self.getH()
        if attrname == 'rotation_y':
            return self.getR()


    @property
    def forward(self):
        return scene.render.getRelativeVector(self, (0, 0, 1))
    @property
    def back(self):
        return scene.render.getRelativeVector(self, (0, 0, -1))
    @property
    def right(self):
        return scene.render.getRelativeVector(self, (1, 0, 0))
    @property
    def left(self):
        return scene.render.getRelativeVector(self, (-1, 0, 0))
    @property
    def up(self):
        return scene.render.getRelativeVector(self, (0, 1, 0))
    @property
    def down(self):
        return scene.render.getRelativeVector(self, (0, -1, 0))



    def reparent_to(self, entity):
        self.wrtReparentTo(entity)
        pos = self.getPos(entity)
        self.position = (pos[0], pos[2], pos[1])
        self.__setattr__('scale', self.getScale(entity))
        # print('parent:', self.parent.name, 'newpos:', self.position)

    def add_script(self, module_name):
        # instance given
        if isinstance(module_name, object) and type(module_name) is not str:
            print('type', type(self))
            module_name.entity = self
            self.scripts.append(module_name)
            return module_name

        # class name given
        if inspect.isclass(module_name):
            class_instance = module_name()
            class_instance.entity = self
            self.scripts.append(class_instance)
            return class_instance

        # module name given
        omn = module_name
        module_name += '.py'
        module_names = (path.join(path.dirname(__file__), module_name),
                        path.join(path.dirname(__file__), 'internal_scripts' , module_name),
                        path.join(path.dirname(path.dirname(__file__)), 'scripts', module_name))

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
                return class_instance
                break
            except Exception as e:
                pass

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
        super().look_at(target)
        # self.setH(self.getH()-180)
        # self.setP(self.getP() * -1)


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
