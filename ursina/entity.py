import sys
import inspect
import importlib
# import random
import glob
from pathlib import Path
from panda3d.core import NodePath
from ursina.vec3 import Vec3
from panda3d.core import Vec4, Vec2
from panda3d.core import TransparencyAttrib
from panda3d.core import Shader
from panda3d.core import TextureStage, TexGenAttrib

from ursina.texture import Texture
from panda3d.core import MovieTexture
from panda3d.core import TextureStage
from panda3d.core import CullFaceAttrib
from ursina import application
from ursina.collider import *
from ursina.mesh import Mesh
from ursina.sequence import Sequence, Func, Wait
from ursina.ursinamath import lerp
from ursina import curve
from ursina.curve import CubicBezier
from ursina.mesh_importer import load_model
from ursina.texture_importer import load_texture
from ursina.string_utilities import camel_to_snake
from textwrap import dedent

from ursina import color
try:
    from ursina import scene
except:
    pass



class Entity(NodePath):

    def __init__(self, add_to_scene_entities=True, **kwargs):
        super().__init__(self.__class__.__name__)

        self.name = camel_to_snake(self.type)
        self.enabled = True     # disabled entities wil not be visible nor run code
        self.visible = True
        self.ignore = False     # if True, will not try to run code
        self.eternal = False    # eternal entities does not get destroyed on scene.clear()
        self.ignore_paused = False
        self.ignore_input = False

        self.parent = scene
        self.add_to_scene_entities = add_to_scene_entities
        if add_to_scene_entities:
            scene.entities.append(self)

        self.model = None       # set model with model='model_name' (without file type extention)
        self.color = color.white
        self.texture = None     # set model with texture='texture_name'. requires a model to be set beforehand.
        self.reflection_map = scene.reflection_map
        self.reflectivity = 0
        self.render_queue = 0
        self.double_sided = False
        self.always_on_top = False

        self.collision = False  # toggle collision without changing collider.
        self.collider = None    # set to 'box'/'sphere'/'mesh' for auto fitted collider.
        self.scripts = list()   # add with add_script(class_instance). will assign an 'entity' variable to the script.
        self.animations = list()
        self.hovered = False    # will return True if mouse hovers entity.

        self.origin = Vec3(0,0,0)
        self.position = Vec3(0,0,0) # can also set self.x, self.y, self.z
        self.rotation = Vec3(0,0,0) # can also set self.rotation_x, self.rotation_y, self.rotation_z
        self.scale = Vec3(1,1,1)    # can also set self.scale_x, self.scale_y, self.scale_z

        self.line_definition = None
        if application.trace_entity_definition and add_to_scene_entities:
            from inspect import getframeinfo, stack
            _stack = stack()
            caller = getframeinfo(_stack[1][0])
            if len(_stack) > 2 and _stack[1].code_context and 'super().__init__()' in _stack[1].code_context[0]:
                caller = getframeinfo(_stack[2][0])

            self.line_definition = caller
            if caller.code_context:
                self.code_context = caller.code_context[0]

                if (self.code_context.count('(') == self.code_context.count(')') and
                ' = ' in self.code_context and not 'name=' in self.code_context
                and not 'Ursina()' in self.code_context):

                    self.name = self.code_context.split(' = ')[0].strip().replace('self.', '')
                    # print('set name to:', self.code_context.split(' = ')[0].strip().replace('self.', ''))

                if application.print_entity_definition:
                    print(f'{Path(caller.filename).name} ->  {caller.lineno} -> {caller.code_context}')


        for key, value in kwargs.items():
            setattr(self, key, value)


    def _list_to_vec(self, value):
        if isinstance(value, (int, float, complex)):
            return Vec3(value, value, value)

        if len(value) % 2 == 0:
            new_value = Vec2()
            for i in range(0, len(value), 2):
                new_value.add_x(value[i])
                new_value.add_y(value[i+1])

        if len(value) % 3 == 0:
            new_value = Vec3()
            for i in range(0, len(value), 3):
                new_value.add_x(value[i])
                new_value.add_y(value[i+1])
                new_value.add_z(value[i+2])

        return new_value


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

        if name == 'eternal':
            for c in self.children:
                c.eternal = value

        if name == 'world_parent':
            self.reparent_to(value)

        if name == 'model':
            if value is None:
                if hasattr(self, 'model') and self.model:
                    self.model.removeNode()
                    # print('removed model')
                object.__setattr__(self, name, value)
                return None

            if isinstance(value, NodePath): # pass procedural model
                if self.model is not None and value != self.model:
                    self.model.removeNode()
                object.__setattr__(self, name, value)

            elif isinstance(value, str): # pass model asset name
                m = load_model(value, application.asset_folder)
                if not m:
                    m = load_model(value, application.internal_models_folder)
                if m:
                    if self.model is not None:
                        self.model.removeNode()
                    object.__setattr__(self, name, m)
                    if isinstance(m, Mesh):
                        m.recipe = value
                    # print('loaded model successively')
                else:
                    print('missing model:', value)
                    return

            if self.model:
                self.model.reparentTo(self)
                self.model.setTransparency(TransparencyAttrib.M_dual)
                self.color = self.color # reapply color after changing model
                self.texture = self.texture # reapply texture after changing model
                self._vert_cache = None
                if isinstance(value, Mesh):
                    if hasattr(value, 'on_assign'):
                        value.on_assign(assigned_to=self)
                return

        if name == 'color' and value is not None:
            if not isinstance(value, Vec4):
                value = Vec4(value[0], value[1], value[2], value[3])


            if self.model:
                self.setColorScaleOff() # prevent inheriting color from parent
                self.model.setColorScale(value)
                object.__setattr__(self, name, value)


        if name == 'texture_scale':
            if self.model and self.texture:
                self.model.setTexScale(TextureStage.getDefault(), value[0], value[1])

        if name == 'texture_offset':
            if self.model and self.texture:
                self.model.setTexOffset(TextureStage.getDefault(), value[0], value[1])
                self.texture = self.texture


        if name == 'collision' and hasattr(self, 'collider') and self.collider:
            if value:
                self.collider.node_path.unstash()
            else:
                self.collider.node_path.stash()

            object.__setattr__(self, name, value)
            return

        if name == 'render_queue':
            if self.model:
                self.model.setBin('fixed', value)

        if name == 'double_sided':
            self.setTwoSided(value)

        if name == 'always_on_top' and value:
            self.set_bin("fixed", 0)
            self.set_depth_write(False)
            self.set_depth_test(False)

        try:
            super().__setattr__(name, value)
        except:
            pass
            # print('failed to set attribiute:', name)


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
            destroy(self)
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
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        if value:
            self.show()
        else:
            self.hide()


    @property
    def collider(self):
        return self._collider

    @collider.setter
    def collider(self, value):
        # destroy existing collider
        if value and hasattr(self, 'collider') and self._collider:
            self._collider.remove()

        self._collider = value

        if value == 'box':
            if self.model:
                self._collider = BoxCollider(entity=self, center=-self.origin, size=self.model_bounds)
            else:
                self._collider = BoxCollider(entity=self)

        elif value == 'sphere':
            self._collider = SphereCollider(entity=self)

        elif value == 'mesh' and self.model:
            self._collider = MeshCollider(entity=self, mesh=self.model, center=-self.origin)

        elif isinstance(value, Mesh):
            self._collider = MeshCollider(entity=self, mesh=value, center=-self.origin)


        self.collision = bool(self.collider)
        return

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        if not self.model:
            self._origin = Vec3(0,0,0)
            return
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.origin_z)

        self._origin = value
        self.model.setPos(-value[0], -value[2], -value[1])


    @property
    def origin_x(self):
        return self.origin[0]
    @origin_x.setter
    def origin_x(self, value):
        self.origin = (value, self.origin_y, self.origin_z)

    @property
    def origin_y(self):
        return self.origin[1]
    @origin_y.setter
    def origin_y(self, value):
        self.origin = (self.origin_x, value, self.origin_z)

    @property
    def origin_z(self):
        return self.origin[2]
    @origin_z.setter
    def origin_z(self, value):
        self.origin = (self.origin_x, self.origin_y, value)

    @property
    def world_position(self):
        return Vec3(self.get_position(render))

    @world_position.setter
    def world_position(self, value):
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.z)

        self.setPos(render, Vec3(value[0], value[2], value[1]))

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

    @position.setter
    def position(self, value):
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.z)

        self.setPos(value[0], value[2], value[1])

    @property
    def x(self):
        return self.getX()
    @x.setter
    def x(self, value):
        self.setX(value)

    @property
    def y(self):
        return self.getZ()
    @y.setter
    def y(self, value):
        self.setZ(value)

    @property
    def z(self):
        return self.getY()
    @z.setter
    def z(self, value):
        self.setY(value)

    @property
    def world_rotation(self):
        rotation = self.getHpr(base.render)
        return Vec3(-rotation[1], -rotation[0], rotation[2])
    @property
    def world_rotation_x(self):
        return -self.getP(base.render)
    @property
    def world_rotation_y(self):
        return -self.getH(base.render)
    @property
    def world_rotation_z(self):
        return self.getR(base.render)

    @property
    def rotation(self):
        rotation = self.getHpr()
        return Vec3(-rotation[1], -rotation[0], rotation[2])

    @rotation.setter
    def rotation(self, value):
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.rotation_z)

        self.setHpr(Vec3(-value[1], -value[0], value[2]))

    @property
    def rotation_x(self):
        return -self.getP()
    @rotation_x.setter
    def rotation_x(self, value):
        self.setP(-value)

    @property
    def rotation_y(self):
        return -self.getH()
    @rotation_y.setter
    def rotation_y(self, value):
        self.setH(-value)

    @property
    def rotation_z(self):
        return self.getR()
    @rotation_z.setter
    def rotation_z(self, value):
        self.setR(value)


    @property
    def world_scale(self):
        scale = self.getScale(base.render)
        return Vec3(scale[0], scale[2], scale[1])
    @world_scale.setter
    def world_scale(self, value):
        if isinstance(value, (int, float, complex)):
            value = (value, value, value)

        self.setScale(base.render, Vec3(value[0], value[2], value[1]))

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

    @scale.setter
    def scale(self, value):
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.scale_z)

        value = [e if e!=0 else .001 for e in value]
        self.setScale(value[0], value[2], value[1])

    @property
    def scale_x(self):
        return self.getScale()[0]
    @scale_x.setter
    def scale_x(self, value):
        self.setScale(value, self.scale_z, self.scale_y)

    @property
    def scale_y(self):
        return self.getScale()[2]
    @scale_y.setter
    def scale_y(self, value):
        self.setScale(self.scale_x, self.scale_z, value)

    @property
    def scale_z(self):
        return self.getScale()[1]
    @scale_z.setter
    def scale_z(self, value):
        self.setScale(self.scale_x, value, self.scale_y)

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

    @property
    def screen_position(self):
        from ursina import camera
        p3 = camera.getRelativePoint(self, Vec3.zero())
        full = camera.lens.getProjectionMat().xform(Vec4(*p3, 1))
        recip_full3 = 1 / full[3]
        p2 = Vec3(full[0], full[1], full[2]) * recip_full3
        screen_pos = Vec3(p2[0]*camera.aspect_ratio/2, p2[1]/2, 0)
        return screen_pos

    @property
    def shader(self):
        return self.getShader()

    @shader.setter
    def shader(self, value):
        if isinstance(value, Shader):
            self.setShader(value)
            return

        if value is None:
            self.setShaderAuto()
            return

        try:
            self.setShader(Shader.load(f'{value}.sha', Shader.SL_Cg))
        except:
            self.setShader(Shader.load(Shader.SL_GLSL, vertex=f'{value}.vert', fragment=f'{value}.frag'))

    @property
    def texture(self):
        if not hasattr(self, '_texture'):
            return None
        return self._texture

    @texture.setter
    def texture(self, value):
        if value is None and self._texture:
            # print('remove texture')
            self._texture = None
            self.setTextureOff(True)
            return

        if value.__class__ is Texture:
            texture = value

        elif isinstance(value, str):
            texture = load_texture(value)
            # print('loaded texture:', texture)
            if texture is None:
                print('no texture:', value)
                return

        if texture.__class__ is MovieTexture:
            self._texture = texture
            self.setTexture(texture)
            return

        self._texture = texture
        if self.model:
            self.model.setTexture(texture._texture, 1)


    @property
    def alpha(self):
        return self.color[3]

    @alpha.setter
    def alpha(self, value):
        if value > 1:
            value = value / 255
        self.color = (self.color.h, self.color.s, self.color.v, value)

    @property
    def reflection_map(self):
        return self._reflection_map

    @reflection_map.setter
    def reflection_map(self, value):
        if value.__class__ is Texture:
            texture = value

        elif isinstance(value, str):
            texture = load_texture(value)

        self._reflection_map = texture


    @property
    def reflectivity(self):
        return self._reflectivity

    @reflectivity.setter
    def reflectivity(self, value):
        self._reflectivity = value

        if value == 0:
            self.texture = None

        if value > 0:
            # if self.reflection_map == None:
            #     self.reflection_map = scene.reflection_map
            #
            # if not self.reflection_map:
            #     print('error setting reflectivity. no reflection map')
            #     return
            if not self.normals:
                self.model.generate_normals()

            # ts = TextureStage('env')
            # ts.setMode(TextureStage.MAdd)
            # self.model.setTexGen(ts, TexGenAttrib.MEyeSphereMap)
            # print('---------------set reflectivity', self.reflection_map)
            # self.model.setTexture(ts, self.reflection_map)

            self.texture = self._reflection_map
            # print('set reflectivity')

    def generate_sphere_map(self, size=512, name=f'sphere_map_{len(scene.entities)}'):
        from ursina import camera
        _name = 'textures/' + name + '.jpg'
        org_pos = camera.position
        camera.position = self.position
        base.saveSphereMap(_name, size=size)
        camera.position = org_pos

        print('saved sphere map:', name)
        self.model.setTexGen(TextureStage.getDefault(), TexGenAttrib.MEyeSphereMap)
        self.reflection_map = name


    def generate_cube_map(self, size=512, name=f'cube_map_{len(scene.entities)}'):
        from ursina import camera
        _name = 'textures/' + name
        org_pos = camera.position
        camera.position = self.position
        base.saveCubeMap(_name+'.jpg', size=size)
        camera.position = org_pos

        print('saved cube map:', name + '.jpg')
        self.model.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldCubeMap)
        self.reflection_map = _name + '#.jpg'
        self.model.setTexture(loader.loadCubeMap(_name + '#.jpg'), 1)


    @property
    def model_bounds(self):
        if self.model:
            bounds = self.model.getTightBounds()
            bounds = Vec3(
                Vec3(bounds[1][0], bounds[1][2], bounds[1][1])  # max point
                - Vec3(bounds[0][0], bounds[0][2], bounds[0][1])    # min point
                )
            return bounds

        return (0,0,0)

    @property
    def bounds(self):
        return Vec3(
            self.model_bounds[0] * self.scale_x,
            self.model_bounds[1] * self.scale_y,
            self.model_bounds[2] * self.scale_z
            )


    def reparent_to(self, entity):
        if entity is not None:
            self.wrtReparentTo(entity)

        self._parent = entity


    def get_position(self, relative_to=scene):
        pos = self.getPos(relative_to)
        return Vec3(pos[0], pos[2], pos[1])


    def set_position(self, value, relative_to=scene):
        self.setPos(relative_to, Vec3(value[0], value[2], value[1]))


    def add_script(self, class_instance):
        if isinstance(class_instance, object) and type(class_instance) is not str:
            class_instance.entity = self
            class_instance.enabled = True
            setattr(self, camel_to_snake(class_instance.__class__.__name__), class_instance)
            self.scripts.append(class_instance)
            # print('added script:', camel_to_snake(name.__class__.__name__))
            return class_instance


    def combine(self, analyze=False, auto_destroy=True):
        from ursina.scripts.combine import combine

        self.model = combine(self, analyze, auto_destroy)
        return self.model


    def flip_faces(self):
        if not hasattr(self, '_vertex_order'):
            self._vertex_order = True

        self._vertex_order = not self._vertex_order
        if self._vertex_order:
            self.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullClockwise))
        else:
            self.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))


    def look_at(self, target, axis='forward'):
        if isinstance(target, Entity):
            target = Vec3(target.world_position)
        super().look_at(render, Vec3(target[0], target[2], target[1]))

        self.rotation += {
        'forward' : (0,0,0),
        'back' :    (180,0,0),
        'right' :   (0,-90,0),
        'left' :    (0,90,0),
        'up' :      (90,0,0),
        'down' :    (-90,0,0),
        }[axis]


    def has_ancestor(self, possible_ancestor):
        p = self
        if isinstance(possible_ancestor, Entity):
            # print('ENTITY')
            for i in range(100):
                if p.parent:
                    if p.parent == possible_ancestor:
                        return True

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


    @property
    def attributes(self):
        return ('name', 'enabled', 'eternal', 'visible', 'parent',
            'origin', 'position', 'rotation', 'scale',
            'model', 'color', 'texture', 'texture_scale', 'texture_offset',

            # 'world_position', 'world_x', 'world_y', 'world_z',
            # 'world_rotation', 'world_rotation_x', 'world_rotation_y', 'world_rotation_z',
            # 'world_scale', 'world_scale_x', 'world_scale_y', 'world_scale_z',
            # 'x', 'y', 'z',
            # 'origin_x', 'origin_y', 'origin_z',
            # 'rotation_x', 'rotation_y', 'rotation_z',
            # 'scale_x', 'scale_y', 'scale_z',

            'render_queue', 'always_on_top', 'collision', 'collider', 'scripts')

#------------
# ANIMATIONS
#------------
    def animate(self, name, value, duration=.1, delay=0, curve=curve.in_expo, resolution=None, interrupt=True, time_step=None):
        s = Sequence(
            Wait(delay),
            Func(self._animate, name, value, duration, curve, resolution, interrupt, time_step)
        )
        s.start()
        return s

    def _animate(self, name, value, duration=.1, curve=curve.in_expo, resolution=None, interrupt=True, time_step=None):
        animator_name = name + '_animator'
        # print('start animating value:', name, animator_name )
        if interrupt and hasattr(self, animator_name):
            try:
                getattr(self, animator_name).pause()
                # print('interrupt', animator_name)
            except:
                pass
        else:
            try:
                getattr(self, animator_name).finish()
            except:
                pass
        setattr(self, animator_name, Sequence(time_step=time_step))
        sequence = getattr(self, animator_name)
        self.animations.append(sequence)
        # sequence.append(Wait(delay))
        if not resolution:
            resolution = max(int(duration * 60), 1)

        for i in range(resolution+1):
            t = i / resolution
            # if isinstance(curve, CubicBezier):
            #     t = curve.calculate(t)
            # else:
            t = curve(t)

            sequence.append(Wait(duration / resolution))
            sequence.append(Func(setattr, self, name, lerp(getattr(self, name), value, t)))

        sequence.start()
        return sequence

    def animate_position(self, value, duration=.1, delay=0, curve=curve.in_expo, resolution=None, interrupt=True, time_step=None):
        x = self.animate('x', value[0], duration, delay, curve, resolution, interrupt, time_step)
        y = self.animate('y', value[1], duration, delay, curve, resolution, interrupt, time_step)
        z = None
        if len(value) > 2:
            z = self.animate('z', value[2], duration, delay, curve, resolution, interrupt, time_step)
        return x, y, z

    def animate_rotation(self, value, duration=.1, delay=0, curve=curve.in_expo, resolution=None, interrupt=True, time_step=None):
        x = self.animate('rotation_x', value[0], duration, delay, curve, resolution, interrupt, time_step)
        y = self.animate('rotation_y', value[1], duration, delay, curve, resolution, interrupt, time_step)
        z = self.animate('rotation_z', value[2], duration, delay, curve, resolution, interrupt, time_step)
        return x, y, z

    def animate_scale(self, value, duration=.1, delay=0, curve=curve.in_expo, resolution=None, interrupt=True, time_step=None):
        if isinstance(value, (int, float, complex)):
            value = Vec3(value, value, value)
        return self.animate('scale', value, duration, delay, curve, resolution, interrupt, time_step)

    # generate animation functions
    for e in ('x', 'y', 'z', 'rotation_x', 'rotation_y', 'rotation_z', 'scale_x', 'scale_y', 'scale_z'):
        exec(dedent(f'''
            def animate_{e}(self, value, duration=.1, delay=0, curve=curve.in_expo, resolution=None, interrupt=True, time_step=None):
                return self.animate('{e}', value, duration, delay, curve, resolution, interrupt, time_step)
        '''))


    def shake(self, duration=.2, magnitude=1, speed=.05, direction=(1,1)):
        s = Sequence()
        self.original_position = self.position
        for i in range(int(duration / speed)):
            s.append(self.posInterval(speed, Vec3(
                self.x + (random.uniform(-.1, .1) * magnitude * direction[0]),
                self.z,
                self.y + (random.uniform(-.1, .1) * magnitude * direction[1]))
            ))
            s.append(self.posInterval(speed, Vec3(
                self.original_position[0],
                self.original_position[2],
                self.original_position[1])
            ))
        s.start()
        return s

    def animate_color(self, value, duration=.1, delay=0, curve=curve.in_expo, resolution=None, interrupt=False, time_step=None):
        return self.animate('color', value, duration, delay, curve, resolution, interrupt, time_step)

    def fade_out(self, value=0, duration=.5, delay=0, curve=curve.in_expo, resolution=None, interrupt=False, time_step=None):
        return self.animate('color', Vec4(self.color[0], self.color[1], self.color[2], value), duration, delay, curve, resolution, interrupt, time_step)

    def fade_in(self, value=1, duration=.5, delay=0, curve=curve.in_expo, resolution=None, interrupt=False, time_step=None):
        return self.animate('color', Vec4(self.color[0], self.color[1], self.color[2], value), duration, delay, curve, resolution, interrupt, time_step)

    def blink(self, value=color.clear, duration=.1, delay=0, curve=curve.in_expo, resolution=None, interrupt=False, time_step=None):
        _original_color = self.color
        if hasattr(self, 'blink_animator'):
            self.blink_animator.finish()
            self.blink_animator.kill()
            # print('finish blink_animator')
        self.blink_animator = Sequence(
            Func(self.animate_color, value, duration*.4, 0, curve, resolution, interrupt),
            Func(self.animate_color, _original_color, duration*.4, duration*.5, curve, resolution, interrupt, time_step)
        )
        self.blink_animator.start()
        return self.blink_animator


if __name__ == '__main__':
    from ursina import *
    app = main.Ursina()

    e = Entity(model='quad', color=color.orange, position=(0,0,1), scale=1.5, rotation=(0,0,45))

    '''example of inheriting Entity'''
    class Player(Entity):
        def __init__(self, **kwargs):
            super().__init__()
            self.model='cube'
            self.color = color.red
            self.scale_y = 2

            for key, value in kwargs.items():
                setattr(self, key, value)

        # input and update functions gets automatically called by the engine
        def input(self, key):
            if key == 'space':
                # self.color = self.color.inverse()
                self.animate_x(2, duration=1)

        def update(self):
            self.x += held_keys['d'] * time.dt * 10
            self.x -= held_keys['a'] * time.dt * 10

    player = Player(x=-1)
    EditorCamera()


    def input(key):
        if key == 'space':
            e.animate('x', -3)

    app.run()
