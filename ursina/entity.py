import sys
import inspect
import importlib
import random
from panda3d.core import PandaNode
from panda3d.core import NodePath
from panda3d.core import GeomNode
from panda3d.core import GeomVertexReader
from panda3d.core import Vec3, Vec4
from panda3d.core import Point3
from panda3d.core import SamplerState
from panda3d.core import TransparencyAttrib
from panda3d.core import Texture, TextureStage
from ursina import application
from ursina.collider import Collider
from ursina.internal_prefabs.mesh import Mesh
from os import path
from panda3d.core import Filename
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.showbase import Loader
from ursina.ursinamath import lerp
from ursina import easing_types
from ursina.easing_types import *
from ursina.useful import *
from ursina.mesh_importer import load_model
from ursina.texture_importer import load_texture

from ursina import color
from ursina import scene


class Entity(NodePath):

    def __init__(self, **kwargs):
        super().__init__(self.__class__.__name__)
        self.name = self.type
        self.enabled = True
        self.visible = True
        self.is_editor = False
        try:
            self.parent = scene
        except:
            print('scene not yet initialized')
        scene.has_changes = True
        self.model = None
        self.color = color.white
        self.texture = None
        try:
            self.texture = camel_to_snake(self.type)
        except:
            pass
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

        if name == 'visible':
            if value == False:
                object.__setattr__(self, '_parent_before_hidden', self.parent)
                self.reparent_to(scene.hidden)
            else:
                try:
                    self.reparent_to(self._parent_before_hidden)
                except:
                    pass
            object.__setattr__(self, name, value)
            return

        if name == 'world_parent':
            self.reparent_to(value)

        if name == 'model':
            if value is None:
                if hasattr(self, 'model') and self.model != None:
                    self.model.removeNode()
                    # print('removed model')
                return None

            if isinstance(value, NodePath): # pass procedural model
                if hasattr(self, 'model'):
                    self.model.removeNode()
                object.__setattr__(self, name, value)

            elif isinstance(value, str): # pass model asset name
                m = load_model(application.asset_folder, value)
                if not m:
                    m = load_model(application.internal_model_folder, value)
                if m:
                    if hasattr(self, 'model'):
                        self.model.removeNode()
                    object.__setattr__(self, name, m)
                    # print('loaded model successively')
                else:
                    print('error loading model:', value)

            if hasattr(self, 'model') and self.model:
                self.model.reparentTo(self)
                # self.model.setColorScaleOff()
                self.model.setTransparency(TransparencyAttrib.MAlpha)
                self._vert_cache = None
                if isinstance(value, Mesh):
                    if hasattr(value, 'on_assign'):
                        value.on_assign(assigned_to=self)
                return
            else:
                print('missing model:', value)

        if name == 'color' and value is not None:
            if hasattr(self, 'model') and self.model:
                vcolors = self.vertex_colors
                if vcolors:
                    for vc in vcolors:
                        if vc != vcolors[0]:
                            self.model.setColorScale(value)     # just tint vertex_colors, untested
                            object.__setattr__(self, name, value)
                            return

                self.model.setColor(value)  # override vertex colors
                object.__setattr__(self, name, value)



        if name == 'texture_scale':
            if self.model and self.texture:
                self.model.setTexScale(TextureStage.getDefault(), value[0], value[1])
                self.texture = self.texture

        if name == 'texture_offset':
            if self.model and self.texture:
                self.model.setTexOffset(TextureStage.getDefault(), value[0], value[1])
                self.texture = self.texture

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
            self.setScale(new_value[0], new_value[2], new_value[1])
            return

        if name == 'scale_x': self.set_scale(value, self.scale_z, self.scale_y)
        if name == 'scale_y': self.set_scale(self.scale_x, self.scale_z, value)
        if name == 'scale_z': self.set_scale(self.scale_x, value, self.scale_y)


        if name == 'collider':
            if value == None and self.collider:
                print('ccccc', type(self.collider))
                # if self.collider:
                from ursina.ursinastuff import destroy
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
    def parent(self):
        try:
            return self._parent
        except:
            return None

    @parent.setter
    def parent(self, value):
        self._parent = value
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

    @property
    def type(self):
        return self.__class__.__name__

    @property
    def types(self):
        return [c.__name__ for c in inspect.getmro(self.__class__)]

    @property
    def world_position(self):
        world_position = self.getPos(render)
        world_position = Vec3(world_position[0], world_position[2], world_position[1])
        return world_position

    @world_position.setter
    def world_position(self, value):
        value = Vec3(value[0], value[2], value[1])
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
    def world_scale(self):
        scale = self.getScale(base.render)
        return Vec3(scale[0], scale[2], scale[1])
    @world_scale.setter
    def world_scale(self, value):
        self.setScale(base.render, Vec3(value[0], value[1], value[2]))

    @property
    def world_scale_x(self):
        return self.getScale(base.render)[0]
    @world_scale_x.setter
    def world_scale_x(self, value):
        self.setScale(base.render, Vec3(value, self.world_scale_z, self.world_scale_y))

    @property
    def world_scale_y(self):
        return self.getScale(base.render)[2]
    @world_scale_y.setter
    def world_scale_y(self, value):
        self.setScale(base.render, Vec3(self.world_scale_x, self.world_scale_z, value))

    @property
    def world_scale_z(self):
        return self.getScale(base.render)[1]
    @world_scale_z.setter
    def world_scale_z(self, value):
        self.setScale(base.render, Vec3(self.world_scale_x, value, self.world_scale_y))

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

    # if name == 'texture':
    @property
    def texture(self):
        return self.model.getTexture()

    @texture.setter
    def texture(self, value):
        if not hasattr(self, 'model') or hasattr(self, 'model') and not self.model:
            return

        if value.__class__ is Texture:
            texture = value

        elif isinstance(value, str):
            t = Filename.fromOsSpecific((load_texture(value)))
            texture = loader.loadTexture(t)
            # print('loaded texture:', t)

        try:
            texture.setMagfilter(SamplerState.FT_nearest)
            texture.setMinfilter(SamplerState.FT_nearest)
            self.model.setTexture(texture, 1)
            self._cached_image = None   # for get_pixel() method
            # print('set texture:', value)
        except:
            pass
            print('no texture:', value)

        if value == None:
            self.model.set_texture_off(True)


    @property
    def texture_name(self):
        return self.texture.getFilename()

    @property
    def texture_path(self):
        return str(self.texture.getFullpath().toOsSpecific())


    @property
    def texture_size(self):
        return (self.width, self.height)

    @property
    def texture_width(self):
        return self.texture.getOrigFileXSize()

    @property
    def texture_height(self):
        return self.texture.getOrigFileYSize()

    @property
    def pixels(self):
        try:
            from PIL import Image
        except Exception as e:
            return e
        from numpy import asarray
        return asarray(Image.open(self.texture_path))


    def get_pixel(self, x, y):
        if not self._cached_image:
            self._cached_image = Image.open(self.texture_path)

        col = self._cached_image.getpixel((x, self.texture_height - y -1))
        if len(col) == 3:
            return (col[0]/255, col[1]/255, col[2]/255, 1)
        else:
            return (col[0]/255, col[1]/255, col[2]/255, col[3]/255)


    @property
    def vertex_data(self):
        if self.model and not self._vert_cache:
            geomNodeCollection = self.model.findAllMatches('**/+GeomNode')
            geomNode = geomNodeCollection[0].node()
            self._vert_cache = geomNode.getGeom(0).getVertexData()
            return self._vert_cache

    @property
    def vertices(self):
        vertex_reader = GeomVertexReader(self.vertex_data, 'vertex')
        vertices = list()
        while not vertex_reader.isAtEnd():
            vertices.append([e for e in vertex_reader.getData3f()])
        return vertices

    @property
    def normals(self):
        vertex_reader = GeomVertexReader(self.vertex_data, 'normal')
        vertices = list()
        while not vertex_reader.isAtEnd():
            vertices.append([e for e in vertex_reader.getData3f()])
        return vertices

    @property
    def uvs(self):
        vertex_reader = GeomVertexReader(self.vertex_data, 'texcoord')
        vertices = list()
        while not vertex_reader.isAtEnd():
            vertices.append([e for e in vertex_reader.getData2f()])
        return vertices

    @property
    def vertex_colors(self):
        try:
            vcol_reader = GeomVertexReader(self.model.findAllMatches('**/+GeomNode')[0].node().getGeom(0).getVertexData(), 'color')
            vcols = list()
            while not vcol_reader.isAtEnd():
                vcols.append([e for e in vcol_reader.getData4f()])
            return vcols
        except:
            print(self.name, '.model has no vertex colors')
            return None


    def reparent_to(self, entity):
        self.wrtReparentTo(entity)
        self._parent = entity


    def add_script(self, module_name):
        # instance given
        if isinstance(module_name, object) and type(module_name) is not str:
            # print('type', type(self))
            module_name.entity = self
            setattr(self, camel_to_snake(module_name.__class__.__name__), module_name)
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

    def remove_script(self, module_name):
        for s in self.scripts:
            if s.__module__ == module_name:
                self.temp_script = s
                self.scripts.remove(s)
                self.__setattr__(module_name, None)
                print('removed:', module_name)


    def look_at(self, target):
        if type(target) is Vec3:
            super().look_at(Vec3(target[0], target[2], target[1]))
            return
        super().look_at(target)


    def get_scripts_of_type(self, type):
        pass


    def has_ancestor(self, possible_ancestor):
        p = self
        if isinstance(possible_ancestor, Entity):
            # print('ENTITY')
            for i in range(100):
                if p.parent:
                    if p.parent == possible_ancestor:
                        return True
                        break
                    p = p.parent

        if isinstance(possible_ancestor, list) or isinstance(possible_ancestor, tuple):
            # print('LIST OR TUPLE')
            for e in possible_ancestor:
                for i in range(100):
                    if p.parent:
                        if p.parent == e:
                            return True
                            break
                        p = p.parent

        elif isinstance(possible_ancestor, str):
            print('CLASS NAME', possible_ancestor)
            for i in range(100):
                if p.parent:
                    if p.parent.__class__.__name__ == possible_ancestor:
                        return True
                        break
                    p = p.parent

        return False


    @property
    def children(self):
        return [e for e in scene.entities if e.parent == self]
        # children_entities = list()
        # for e in scene.entities:
        #     if e.parent == self:
        #         children_entities.append(e)
        #
        #
        # return children_entities

#------------
# ANIMATIONS
#------------
    def animate(self, name, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None, interrupt=True):
        animator_name = name + '_animator'
        # print('start animating value:', name, animator_name )
        if interrupt and hasattr(self, animator_name):
            try:
                getattr(self, animator_name).pause()
                # print('interrupt', animator_name)
            except:
                pass
        setattr(self, animator_name, Sequence())
        sequence = getattr(self, animator_name)
        sequence.append(Wait(delay))
        if not resolution:
            resolution = int(duration * 60)

        for i in range(resolution+1):
            t = i / resolution
            if hasattr(easing_types, curve):
                t = getattr(easing_types, curve)(t)
            else:
                t = getattr(easing_types, 'ease_in_expo')(t)
            sequence.append(Wait(duration / resolution))
            sequence.append(Func(setattr, self, name, lerp(getattr(self, name), value, t)))

        sequence.start()
        return sequence

    def animate_position(self, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None, interrupt=True):
        self.animate('x', value[0], duration, delay, curve, resolution, interrupt)
        self.animate('y', value[1], duration, delay, curve, resolution, interrupt)
        self.animate('z', value[2], duration, delay, curve, resolution, interrupt)
    def animate_x(self, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None, interrupt=True):
        self.animate('x', value, duration, delay, curve, resolution, interrupt)
    def animate_y(self, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None, interrupt=True):
        self.animate('y', value, duration, delay, curve, resolution, interrupt)
    def animate_z(self, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None, interrupt=True):
        self.animate('z', value, duration, delay, curve, resolution, interrupt)


    def animate_rotation(self, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None, interrupt=True):
        self.animate('rotation_x', value[0], duration, delay, curve, resolution, interrupt)
        self.animate('rotation_y', value[1], duration, delay, curve, resolution, interrupt)
        self.animate('rotation_z', value[2], duration, delay, curve, resolution, interrupt)
    def animate_rotation_x(self, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None, interrupt=True):
        self.animate('rotation_x', value, duration, delay, curve, resolution, interrupt)
    def animate_rotation_y(self, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None, interrupt=True):
        self.animate('rotation_y', value, duration, delay, curve, resolution, interrupt)
    def animate_rotation_z(self, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None, interrupt=True):
        self.animate('rotation_z', value, duration, delay, curve, resolution, interrupt)

    def animate_scale(self, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None, interrupt=True):
        self.animate('scale', value, duration, delay, curve, resolution, interrupt)
    def animate_scale_x(self, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None, interrupt=True):
        self.animate('scale_x', value, duration, delay, curve, resolution, interrupt)
    def animate_scale_y(self, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None, interrupt=True):
        self.animate('scale_y', value, duration, delay, curve, resolution, interrupt)
    def animate_scale_z(self, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None, interrupt=True):
        self.animate('scale_z', value, duration, delay, curve, resolution, interrupt)


    def shake(self, duration=.2, magnitude=1, speed=.05):
        s = Sequence()
        self.original_position = self.position
        for i in range(int(duration / speed)):
            s.append(self.posInterval(speed, Point3(
                self.x + (random.uniform(-.1, .1) * magnitude),
                self.z,
                self.y + (random.uniform(-.1, .1) * magnitude))
            ))
            s.append(self.posInterval(speed, Point3(
                self.original_position[0],
                self.original_position[2],
                self.original_position[1])
            ))
        s.start()

    def animate_color(self, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None):
        from ursina.ursinastuff import invoke
        invoke(self._animate_color, value, duration, curve, resolution, delay=delay)

    def _animate_color(self, value, duration=.1, curve='ease_in_expo', resolution=None):
        if hasattr(self, 'color_animator') and self.color_animator:
            print('pause color animator')
            self.color_animator.pause()
        print('anim color')
        self.color_animator = Sequence()

        if not resolution:
            resolution = int(duration * 60)

        for i in range(resolution+1):
            t = i / resolution
            if hasattr(easing_types, curve):
                t = getattr(easing_types, curve)(t)
            else:
                t = getattr(easing_types, 'ease_in_expo')(t)
            self.color_animator.append(Wait(duration / resolution))
            new_color = Vec4(
                lerp(self.color[0], value[0], t),
                lerp(self.color[1], value[1], t),
                lerp(self.color[2], value[2], t),
                lerp(self.color[3], value[3], t)
                )
            # self.color_animator.append(Func(self.model.setColorScale, new_color))
            self.color_animator.append(Func(self.set_color, new_color))

        self.color_animator.start()
        return self.color_animator

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
        self.animate_y = 1
        self.frame = 0
        self.d = False

    def input(self, key):
        if key == '1':
            e.shake()

        if key == 'x':
            self.move = -self.move
            e.animate_x(self.x + self.move)

        if key == 'y':
            e.animate_y(self.y + 1)

        if key == 'd':
            self.d = True
        if key == 'd up':
            self.d = False

        if key == 'space':
            e.animate_y(e.y + 2.5, .7)
            invoke(self.fall, delay=.5)

    def fall(self):
        print('fall')
        e.animate_y(0, duration=.5)

    def update(self):
        self.frame += 1
        if self.frame >= 4:
            if self.d:
                e.animate_x(self.x + 1, 1/60 * 4)
            self.frame = 0


class TestClass(Entity):
    def __init__(self):
        super().__init__()
    def on_hover(self):
        print('yo')

if __name__ == '__main__':
    from ursina import main
    from ursinastuff import invoke

    app = main.Ursina()


    #
    e = Entity(model='quad', color=color.red, collider='box', texture='white_cube')
    # e.animate_position(e.position + e.up, duration=1, delay=1, curve='ease_in_expo')
    # e.animate_color(color.yellow, duration=.5, delay=1)
    # e.animate('x', 2, 1)
    # e.animate_position((2,2,2), 1)
    e.animate_scale((0,0,0), 1)
    # printvar(e.world_position)
    #
    # e.world_x = 1
    # e.world_y = 1
    # e.world_z = 1
    # printvar(e.world_x)
    # printvar(e.world_y)
    # printvar(e.world_z)

    # t = TestClass()
    # # t.parent = scene.ui
    # # import mouse
    # t.model = 'cube'
    # t.collider = 'box'
    my_parent = Entity()
    my_tuple = (Entity(), Entity())
    my_class_name = 'TestClass'

    t = Entity(parent = e)
    # printvar(t.has_ancestor(e))
    # printvar(t.has_ancestor(my_tuple))
    # print('!!!!!!', type(Entity))
    # print('....', Entity.__class__)
    # printvar(isinstance(t.parent, Entity.__class__))
    # printvar(t.has_ancestor(Entity))


    # e.model = None

    # shake_tester = ShakeTester()
    app.run()
