import sys
import importlib
import glob
from pathlib import Path
from panda3d.core import NodePath
from ursina.vec2 import Vec2
from ursina.vec3 import Vec3
from ursina.vec4 import Vec4
from panda3d.core import Quat
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
from ursina import mesh_importer
from ursina.mesh_importer import load_model
from ursina.texture_importer import load_texture
from ursina.string_utilities import camel_to_snake
from textwrap import dedent
from panda3d.core import Shader as Panda3dShader
from ursina import shader
from ursina.shader import Shader
from ursina.string_utilities import print_info, print_warning

from ursina import color
from ursina.color import Color
try:
    from ursina.scene import instance as scene
except:
    pass



class Entity(NodePath):

    rotation_directions = (-1,-1,1)
    default_shader = None

    def __init__(self, add_to_scene_entities=True, **kwargs):
        super().__init__(self.__class__.__name__)

        self.name = camel_to_snake(self.type)
        self.enabled = True     # disabled entities will not be visible nor run code.
        self.visible = True
        self.ignore = False     # if True, will not try to run code.
        self.eternal = False    # eternal entities does not get destroyed on scene.clear()
        self.ignore_paused = False      # if True, will still run when application is paused. useful when making a pause menu for example.
        self.ignore_input = False

        self.parent = scene     # default parent is scene, which means it's in 3d space. to use UI space, set the parent to camera.ui instead.
        self.add_to_scene_entities = add_to_scene_entities # set to False to be ignored by the engine, but still get rendered.
        if add_to_scene_entities:
            scene.entities.append(self)

        self.model = None       # set model with model='model_name' (without file type extension)
        self.color = color.white
        self.texture = None     # set model with texture='texture_name'. requires a model to be set beforehand.
        self.render_queue = 0
        self.double_sided = False
        if Entity.default_shader:
            self.shader = Entity.default_shader

        self.collision = False  # toggle collision without changing collider.
        self.collider = None    # set to 'box'/'sphere'/'mesh' for auto fitted collider.
        self.scripts = []   # add with add_script(class_instance). will assign an 'entity' variable to the script.
        self.animations = []
        self.hovered = False    # will return True if mouse hovers entity.

        self.origin = Vec3(0,0,0)
        self.position = Vec3(0,0,0) # right, up, forward. can also set self.x, self.y, self.z
        self.rotation = Vec3(0,0,0) # can also set self.rotation_x, self.rotation_y, self.rotation_z
        self.scale = Vec3(1,1,1)    # can also set self.scale_x, self.scale_y, self.scale_z

        self.line_definition = None # returns a Traceback(filename, lineno, function, code_context, index).
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

        # make sure things get set in the correct order. both colliders and texture need the model to be set first.
        for key in ('model', 'origin', 'origin_x', 'origin_y', 'origin_z', 'collider', 'shader', 'texture', 'texture_scale', 'texture_offset'):
            if key in kwargs:
                setattr(self, key, kwargs[key])
                del kwargs[key]

        for key, value in kwargs.items():
            setattr(self, key, value)

        if self.enabled and hasattr(self, 'on_enable'):
            if isinstance(self.on_enable, Sequence):
                self.on_enable.start()
            elif callable(self.on_enable):
                self.on_enable()

        elif not self.enabled and hasattr(self, 'on_disable'):
            if isinstance(self.on_disable, Sequence):
                self.on_disable.start()
            elif callable(self.on_disable):
                self.on_disable()


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


    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


    @property
    def enabled(self):
        if not hasattr(self, '_enabled'):
            return True
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value and hasattr(self, 'on_enable') and not self.enabled:
            if isinstance(self.on_enable, Sequence):
                self.on_enable.start()
            elif callable(self.on_enable):
                self.on_enable()

        elif value == False and hasattr(self, 'on_disable') and self.enabled:
            if isinstance(self.on_disable, Sequence):
                self.on_disable.start()
            elif callable(self.on_disable):
                self.on_disable()


        if value == True:
            if hasattr(self, 'is_singleton') and not self.is_singleton():
                self.unstash()
        else:
            if hasattr(self, 'is_singleton') and not self.is_singleton():
                self.stash()

        self._enabled = value


    def __setattr__(self, name, value):
        if name == 'eternal':
            for c in self.children:
                c.eternal = value

        elif name == 'model':
            if value is None:
                if hasattr(self, 'model') and self.model:
                    self.model.removeNode()
                    # print('removed model')
                object.__setattr__(self, name, value)
                return None

            if isinstance(value, NodePath): # pass procedural model
                if self.model is not None and value != self.model:
                    self.model.detachNode()
                object.__setattr__(self, name, value)

            elif isinstance(value, str): # pass model asset name
                m = load_model(value, application.asset_folder)
                if not m:
                    m = load_model(value, application.internal_models_compressed_folder)
                if m:
                    if self.model is not None:
                        self.model.removeNode()

                    m.name = value
                    m.setPos(Vec3(0,0,0))
                    object.__setattr__(self, name, m)
                    # if not value in mesh_importer.imported_meshes:
                    #     print_info('loaded model successfully:', value)
                else:
                    if application.raise_exception_on_missing_model:
                        raise ValueError(f"missing model: '{value}'")

                    print_warning(f"missing model: '{value}'")
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

        elif name == 'color' and value is not None:
            if isinstance(value, str):
                value = color.hex(value)

            if not isinstance(value, Vec4):
                value = Vec4(value[0], value[1], value[2], value[3])


            if self.model:
                self.model.setColorScaleOff() # prevent inheriting color from parent
                self.model.setColorScale(value)
                object.__setattr__(self, name, value)


        elif name == 'collision' and hasattr(self, 'collider') and self.collider:
            if value:
                self.collider.node_path.unstash()
            else:
                self.collider.node_path.stash()

            object.__setattr__(self, name, value)
            return

        elif name == 'render_queue':
            if self.model:
                self.model.setBin('fixed', value)

        elif name == 'double_sided':
            self.setTwoSided(value)

        elif hasattr(self, '_shader') and self.shader and name in self._shader.default_input:
            # print('set shader input:', name, value)
            object.__setattr__(self, name, value)
            self.set_shader_input(name, value)


        try:
            super().__setattr__(name, value)
        except:
            pass
            # print('failed to set attribute:', name)


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
                raise ValueError(f'invalid parent: value')

    @property
    def world_parent(self):
        return self.parent

    @world_parent.setter
    def world_parent(self, value):  # change the parent, but keep position, rotation and scale
        self.reparent_to(value)


    @property
    def type(self): # get class name.
        return self.__class__.__name__

    @property
    def types(self): # get all class names including those this inhertits from.
        from inspect import getmro
        return [c.__name__ for c in getmro(self.__class__)]


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
    def visible_self(self): # set visibility of self, without affecting children.
        if not hasattr(self, '_visible_self'):
            return True
        return self._visible_self

    @visible_self.setter
    def visible_self(self, value):
        self._visible_self = value
        if not self.model:
            return
        if value:
            self.model.show()
        else:
            self.model.hide()


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
                # start, end = self.model.getTightBounds()
                # model_center = (start + end) / 2
                self._collider = BoxCollider(entity=self, center=-self.origin, size=self.model_bounds)
            else:
                self._collider = BoxCollider(entity=self)
            self._collider.name = value

        elif value == 'sphere':
            self._collider = SphereCollider(entity=self, center=-self.origin)
            self._collider.name = value

        elif value == 'mesh' and self.model:
            self._collider = MeshCollider(entity=self, mesh=None, center=-self.origin)
            self._collider.name = value

        elif isinstance(value, Mesh):
            self._collider = MeshCollider(entity=self, mesh=value, center=-self.origin)

        elif isinstance(value, str):
            m = load_model(value)
            if not m:
                return
            self._collider = MeshCollider(entity=self, mesh=m, center=-self.origin)
            self._collider.name = value


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
        self.model.setPos(-value[0], -value[1], -value[2])


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

        self.setPos(render, Vec3(value[0], value[1], value[2]))

    @property
    def world_x(self):
        return self.getX(render)
    @property
    def world_y(self):
        return self.getY(render)
    @property
    def world_z(self):
        return self.getZ(render)

    @world_x.setter
    def world_x(self, value):
        self.setX(render, value)
    @world_y.setter
    def world_y(self, value):
        self.setY(render, value)
    @world_z.setter
    def world_z(self, value):
        self.setZ(render, value)

    @property
    def position(self):
        return Vec3(*self.getPos())

    @position.setter
    def position(self, value):
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.z)

        self.setPos(value[0], value[1], value[2])

    @property
    def x(self):
        return self.getX()
    @x.setter
    def x(self, value):
        self.setX(value)

    @property
    def y(self):
        return self.getY()
    @y.setter
    def y(self, value):
        self.setY(value)

    @property
    def z(self):
        return self.getZ()
    @z.setter
    def z(self, value):
        self.setZ(value)

    @property
    def X(self):    # shortcut for int(entity.x)
        return int(self.x)
    @property
    def Y(self):    # shortcut for int(entity.y)
        return int(self.y)
    @property
    def Z(self):    # shortcut for int(entity.z)
        return int(self.z)

    @property
    def world_rotation(self):
        rotation = self.getHpr(scene)
        return Vec3(rotation[1], rotation[0], rotation[2]) * Entity.rotation_directions

    @world_rotation.setter
    def world_rotation(self, value):
        self.setHpr(scene, Vec3(value[1], value[0], value[2]) * Entity.rotation_directions)

    @property
    def world_rotation_x(self):
        return self.world_rotation[0]

    @world_rotation_x.setter
    def world_rotation_x(self, value):
        self.world_rotation = Vec3(value, self.world_rotation[1], self.world_rotation[2])

    @property
    def world_rotation_y(self):
        return self.world_rotation[1]

    @world_rotation_y.setter
    def world_rotation_y(self, value):
        self.world_rotation = Vec3(self.world_rotation[0], value, self.world_rotation[2])

    @property
    def world_rotation_z(self):
        return self.world_rotation[2]

    @world_rotation_z.setter
    def world_rotation_z(self, value):
        self.world_rotation = Vec3(self.world_rotation[0], self.world_rotation[1], value)

    @property
    def rotation(self):
        rotation = self.getHpr()
        return Vec3(rotation[1], rotation[0], rotation[2]) * Entity.rotation_directions

    @rotation.setter
    def rotation(self, value):
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.rotation_z)

        self.setHpr(Vec3(value[1], value[0], value[2]) * Entity.rotation_directions)

    @property
    def rotation_x(self):
        return self.rotation.x
    @rotation_x.setter
    def rotation_x(self, value):
        self.rotation = Vec3(value, self.rotation[1], self.rotation[2])

    @property
    def rotation_y(self):
        return self.rotation.y
    @rotation_y.setter
    def rotation_y(self, value):
        self.rotation = Vec3(self.rotation[0], value, self.rotation[2])

    @property
    def rotation_z(self):
        return self.rotation.z
    @rotation_z.setter
    def rotation_z(self, value):
        self.rotation = Vec3(self.rotation[0], self.rotation[1], value)

    @property
    def quaternion(self):
        return self.get_quat()
    @quaternion.setter
    def quaternion(self, value):
        self.set_quat(value)

    @property
    def world_scale(self):
        return Vec3(*self.getScale(base.render))
    @world_scale.setter
    def world_scale(self, value):
        if isinstance(value, (int, float, complex)):
            value = Vec3(value, value, value)

        self.setScale(base.render, value)

    @property
    def world_scale_x(self):
        return self.getScale(base.render)[0]
    @world_scale_x.setter
    def world_scale_x(self, value):
        self.setScale(base.render, Vec3(value, self.world_scale_y, self.world_scale_z))

    @property
    def world_scale_y(self):
        return self.getScale(base.render)[1]
    @world_scale_y.setter
    def world_scale_y(self, value):
        self.setScale(base.render, Vec3(self.world_scale_x, value, self.world_scale_z))

    @property
    def world_scale_z(self):
        return self.getScale(base.render)[2]
    @world_scale_z.setter
    def world_scale_z(self, value):
        self.setScale(base.render, Vec3(self.world_scale_x, self.world_scale_y, value))

    @property
    def scale(self):
        scale = self.getScale()
        return Vec3(scale[0], scale[1], scale[2])

    @scale.setter
    def scale(self, value):
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.scale_z)

        value = [e if e!=0 else .001 for e in value]
        self.setScale(value[0], value[1], value[2])

    @property
    def scale_x(self):
        return self.scale[0]
    @scale_x.setter
    def scale_x(self, value):
        self.setScale(value, self.scale_y, self.scale_z)

    @property
    def scale_y(self):
        return self.scale[1]
    @scale_y.setter
    def scale_y(self, value):
        self.setScale(self.scale_x, value, self.scale_z)

    @property
    def scale_z(self):
        return self.scale[2]
    @scale_z.setter
    def scale_z(self, value):
        self.setScale(self.scale_x, self.scale_y, value)

    @property
    def transform(self): # get/set position, rotation and scale
        return (self.position, self.rotation, self.scale)
    @transform.setter
    def transform(self, value):
        self.position, self.rotation, self.scale = value

    @property
    def world_transform(self): # get/set world_position, world_rotation and world_scale
        return (self.world_position, self.world_rotation, self.world_scale)
    @world_transform.setter
    def world_transform(self, value):
        self.world_position, self.world_rotation, self.world_scale = value


    @property
    def forward(self): # get forward direction.
        return Vec3(*render.getRelativeVector(self, (0, 0, 1)))
    @property
    def back(self): # get backwards direction.
        return -self.forward
    @property
    def right(self): # get right direction.
        return Vec3(*render.getRelativeVector(self, (1, 0, 0)))
    @property
    def left(self): # get left direction.
        return -self.right
    @property
    def up(self): # get up direction.
        return Vec3(*render.getRelativeVector(self, (0, 1, 0)))
    @property
    def down(self): # get down direction.
        return -self.up

    @property
    def screen_position(self): # get screen position(ui space) from world space.
        from ursina import camera
        p3 = camera.getRelativePoint(self, Vec3.zero())
        full = camera.lens.getProjectionMat().xform(Vec4(*p3, 1))
        recip_full3 = 1 / full[3]
        p2 = Vec3(full[0], full[1], full[2]) * recip_full3
        screen_pos = Vec3(p2[0]*camera.aspect_ratio/2, p2[1]/2, 0)
        return screen_pos

    @property
    def shader(self):
        if not hasattr(self, '_shader'):
            return None
        return self._shader

    @shader.setter
    def shader(self, value):
        if value is None:
            self._shader = value
            self.setShaderAuto()
            return

        if isinstance(value, Panda3dShader): #panda3d shader
            self._shader = value
            self.setShader(value)
            return

        if isinstance(value, str):
            if not value in shader.imported_shaders:
                print_warning('missing shader:', value)
                return

            value = shader.imported_shaders[value]

        if isinstance(value, Shader):
            self._shader = value
            if not value.compiled:
                value.compile()

            self.setShader(value._shader)
            value.entity = self

            for key, value in value.default_input.items():
                if callable(value):
                    value = value()
                self.set_shader_input(key, value)

            return

        raise ValueError(f'{value} is not a Shader')



    def set_shader_input(self, name, value):
        if isinstance(value, Texture):
            value = value._texture    # make sure to send the panda3d texture to the shader

        super().set_shader_input(name, value)


    @property
    def texture(self):
        if not hasattr(self, '_texture'):
            return None
        return self._texture

    @texture.setter
    def texture(self, value):
        if value is None and self._texture:
            # print('remove texture')
            self.model.clearTexture()
            self._texture = None
            return

        if value.__class__ is Texture:
            texture = value

        elif isinstance(value, str):
            texture = load_texture(value)
            # print('loaded texture:', texture)
            if texture is None:
                if application.raise_exception_on_missing_texture:
                    raise ValueError(f"missing texture: '{value}'")

                print_warning(f"missing texture: '{value}'")
                return

        self.model.setTextureOff(False)
        if texture.__class__ is MovieTexture:
            self._texture = texture
            self.model.setTexture(texture, 1)
            return

        self._texture = texture
        if self.model:
            self.model.setTexture(texture._texture, 1)


    @property
    def texture_scale(self):
        if not hasattr(self, '_texture_scale'):
            return Vec2(1,1)
        return self._texture_scale
    @texture_scale.setter
    def texture_scale(self, value):
        self._texture_scale = value
        if self.model and self.texture:
            self.model.setTexScale(TextureStage.getDefault(), value[0], value[1])
            self.set_shader_input('texture_scale', value)

    @property
    def texture_offset(self):
        if not hasattr(self, '_texture_offset'):
            return Vec2(0,0)
        return self._texture_offset

    @texture_offset.setter
    def texture_offset(self, value):
        if self.model and self.texture:
            self.model.setTexOffset(TextureStage.getDefault(), value[0], value[1])
            self.texture = self.texture
            self.set_shader_input('texture_offset', value)
        self._texture_offset = value

    @property
    def tileset_size(self):         # if the texture is a tileset, say how many tiles there are so it only use one tile of the texture, e.g. tileset_size=[8,4]
        return self._tileset_size
    @tileset_size.setter
    def tileset_size(self, value):
        self._tileset_size = value
        self.texture_scale = Vec2(1/value[0], 1/value[1])

    @property
    def tile_coordinate(self):      # set the tile coordinate, starts in the lower left.
        return self._tile_coordinate
    @tile_coordinate.setter
    def tile_coordinate(self, value):
        self._tile_coordinate = value
        self.texture_offset = Vec2(value[0] / self.tileset_size[0], value[1] / self.tileset_size[1])


    @property
    def alpha(self):
        return self.color[3]

    @alpha.setter
    def alpha(self, value):
        if value > 1:
            value = value / 255
        self.color = color.color(self.color.h, self.color.s, self.color.v, value)


    @property
    def always_on_top(self):
        return self._always_on_top
    @always_on_top.setter
    def always_on_top(self, value):
        self._always_on_top = value
        self.set_bin("fixed", 0)
        self.set_depth_write(not value)
        self.set_depth_test(not value)

    @property
    def unlit(self):
        if not hasattr(self, '_unlit'):
            return False
        return self._unlit

    @unlit.setter
    def unlit(self, value):
        self._unlit = value
        self.setLightOff(value)

    @property
    def billboard(self): # set to True to make this Entity always face the camera.
        return self._billboard

    @billboard.setter
    def billboard(self, value):
        self._billboard = value
        if value:
            self.setBillboardPointEye(value)


    def generate_sphere_map(self, size=512, name=f'sphere_map_{len(scene.entities)}'):
        from ursina import camera
        _name = 'textures/' + name + '.jpg'
        org_pos = camera.position
        camera.position = self.position
        base.saveSphereMap(_name, size=size)
        camera.position = org_pos

        # print('saved sphere map:', name)
        self.model.setTexGen(TextureStage.getDefault(), TexGenAttrib.MEyeSphereMap)
        self.reflection_map = name


    def generate_cube_map(self, size=512, name=f'cube_map_{len(scene.entities)}'):
        from ursina import camera
        _name = 'textures/' + name
        org_pos = camera.position
        camera.position = self.position
        base.saveCubeMap(_name+'.jpg', size=size)
        camera.position = org_pos

        # print('saved cube map:', name + '.jpg')
        self.model.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldCubeMap)
        self.reflection_map = _name + '#.jpg'
        self.model.setTexture(loader.loadCubeMap(_name + '#.jpg'), 1)


    @property
    def model_bounds(self):
        if self.model:
            bounds = self.model.getTightBounds()
            bounds = Vec3(
                Vec3(bounds[1][0], bounds[1][1], bounds[1][2])  # max point
                - Vec3(bounds[0][0], bounds[0][1], bounds[0][2])    # min point
                )
            return bounds

        return Vec3(0,0,0)

    @property
    def model_center(self):
        if not self.model:
            return Vec3(0,0,0)
        return self.model.getTightBounds().getCenter()

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
        return self.getPos(relative_to)


    def set_position(self, value, relative_to=scene):
        self.setPos(relative_to, Vec3(value[0], value[1], value[2]))


    def rotate(self, value, relative_to=None):  # rotate around local axis.
        if not relative_to:
            relative_to = self

        self.setHpr(relative_to, Vec3(value[1], value[0], value[2]) * Entity.rotation_directions)


    def add_script(self, class_instance):
        if isinstance(class_instance, object) and type(class_instance) is not str:
            class_instance.entity = self
            class_instance.enabled = True
            setattr(self, camel_to_snake(class_instance.__class__.__name__), class_instance)
            self.scripts.append(class_instance)
            # print('added script:', camel_to_snake(name.__class__.__name__))
            return class_instance


    def combine(self, analyze=False, auto_destroy=True, ignore=[]):
        from ursina.scripts.combine import combine

        self.model = combine(self, analyze, auto_destroy, ignore)
        return self.model


    @property
    def flipped_faces(self):
        return self._flipped_faces
    @flipped_faces.setter
    def flipped_faces(self, value):
        self._flipped_faces = value
        if value:
            self.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullClockwise))
        else:
            self.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))


    def look_at(self, target, axis='forward'):
        from panda3d.core import Quat
        if not isinstance(target, Entity):
            target = Vec3(*target)

        self.lookAt(target, Vec3(0,0,1))
        if axis == 'forward':
            return

        rotation_offset = {
            'back'    : Quat(0,0,1,0),
            'down'    : Quat(-.707,.707,0,0),
            'up'      : Quat(-.707,-.707,0,0),
            'right'   : Quat(-.707,0,.707,0),
            'left'    : Quat(-.707,0,-.707,0),
            }[axis]

        self.setQuat(rotation_offset * self.getQuat())


    def look_at_2d(self, target, axis='z'):
        from math import degrees, atan2
        if isinstance(target, Entity):
            target = Vec3(target.world_position)

        pos = target - self.world_position
        if axis == 'z':
            self.rotation_z = degrees(atan2(pos[0], pos[1]))
        elif axis == 'y':
            self.rotation_y = degrees(atan2(pos[0], pos[2]))
        elif axis == 'x':
            self.rotation_x = degrees(atan2(pos[1], pos[2]))


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
    def attributes(self): # attribute names. used by duplicate().
        return ('name', 'enabled', 'eternal', 'visible', 'parent',
            'origin', 'position', 'rotation', 'scale',
            'model', 'color', 'texture', 'texture_scale', 'texture_offset',
            'render_queue', 'always_on_top', 'collider', 'collision', 'scripts')

    def __str__(self):
        return self.name

    def __repr__(self):
        default_values = {
            # 'parent':scene,
            'name':'entity', 'enabled':True, 'eternal':False, 'position':Vec3(0,0,0), 'rotation':Vec3(0,0,0), 'scale':Vec3(1,1,1), 'model':None, 'origin':Vec3(0,0,0),
            'shader':None, 'texture':None, 'color':color.white, 'collider':None}

        changes = []
        for key, value in default_values.items():
            if not getattr(self, key) == default_values[key]:
                if key == 'model' and hasattr(self.model, 'name'):
                    changes.append(f"model='{getattr(self, key).name}', ")
                    continue
                if key == 'shader' and self.shader:
                    changes.append(f"shader='{getattr(self, key).name}', ")
                    continue
                if key == 'texture':
                    changes.append(f"texture='{getattr(self, key).name.split('.')[0]}', ")
                    continue
                if key == 'collider':
                    changes.append(f"collider='{getattr(self, key).name}', ")
                    continue

                value = getattr(self, key)
                if isinstance(value, str):
                    value = f"'{repr(value)}'"

                changes.append(f"{key}={value}, ")

        return f'{__class__.__name__}(' +  ''.join(changes) + ')'


    def __deepcopy__(self, memo):
        return eval(repr(self))


#------------
# ANIMATIONS
#------------
    def animate(self, name, value, duration=.1, delay=0, curve=curve.in_expo, loop=False, resolution=None, interrupt='kill', time_step=None, auto_destroy=True):
        if duration == 0 and delay == 0:
            setattr(self, name, value)
            return None

        if delay:
            from ursina.ursinastuff import invoke
            return invoke(self.animate, name, value, duration=duration, curve=curve, loop=loop, resolution=resolution, time_step=time_step, auto_destroy=auto_destroy, delay=delay)

        animator_name = name + '_animator'
        # print('start animating value:', name, animator_name )
        if interrupt and hasattr(self, animator_name):
            getattr(getattr(self, animator_name), interrupt)() # call kill() or finish() depending on what the interrupt value is.
            # print('interrupt', interrupt, animator_name)

        sequence = Sequence(loop=loop, time_step=time_step, auto_destroy=auto_destroy)
        setattr(self, animator_name, sequence)
        self.animations.append(sequence)

        if not resolution:
            resolution = max(int(duration * 60), 1)

        for i in range(resolution+1):
            t = i / resolution
            t = curve(t)

            sequence.append(Wait(duration / resolution))
            sequence.append(Func(setattr, self, name, lerp(getattr(self, name), value, t)))

        sequence.start()
        return sequence

    def animate_position(self, value, duration=.1, **kwargs):
        x = self.animate('x', value[0], duration,  **kwargs)
        y = self.animate('y', value[1], duration,  **kwargs)
        z = None
        if len(value) > 2:
            z = self.animate('z', value[2], duration, **kwargs)
        return x, y, z

    def animate_rotation(self, value, duration=.1,  **kwargs):
        x = self.animate('rotation_x', value[0], duration,  **kwargs)
        y = self.animate('rotation_y', value[1], duration,  **kwargs)
        z = self.animate('rotation_z', value[2], duration,  **kwargs)
        return x, y, z

    def animate_scale(self, value, duration=.1, **kwargs):
        if isinstance(value, (int, float, complex)):
            value = Vec3(value, value, value)
        elif isinstance(value, tuple) and len(value) == 2:
            value = Vec3(*value, self.z)

        return self.animate('scale', value, duration,  **kwargs)

    # generate animation functions
    for e in ('x', 'y', 'z', 'rotation_x', 'rotation_y', 'rotation_z', 'scale_x', 'scale_y', 'scale_z'):
        exec(dedent(f'''
            def animate_{e}(self, value, duration=.1, delay=0, **kwargs):
                return self.animate('{e}', value, duration=duration, delay=delay, **kwargs)
        '''))


    def shake(self, duration=.2, magnitude=1, speed=.05, direction=(1,1)):
        import random
        s = Sequence()
        original_position = self.world_position
        for i in range(int(duration / speed)):
            s.append(Func(self.set_position,
                Vec3(
                    original_position[0] + (random.uniform(-.1, .1) * magnitude * direction[0]),
                    original_position[1] + (random.uniform(-.1, .1) * magnitude * direction[1]),
                    original_position[2],
                )))
            s.append(Wait(speed))
            s.append(Func(setattr, self, 'world_position', original_position))

        self.animations.append(s)
        s.start()
        return s

    def animate_color(self, value, duration=.1, interrupt='finish', **kwargs):
        return self.animate('color', value, duration, interrupt=interrupt, **kwargs)

    def fade_out(self, value=0, duration=.5, **kwargs):
        return self.animate('color', Vec4(self.color[0], self.color[1], self.color[2], value), duration,  **kwargs)

    def fade_in(self, value=1, duration=.5, **kwargs):
        return self.animate('color', Vec4(self.color[0], self.color[1], self.color[2], value), duration,  **kwargs)

    def blink(self, value=color.clear, duration=.1, delay=0, curve=curve.in_expo_boomerang, interrupt='finish', **kwargs):
        return self.animate_color(value, duration=duration, delay=delay, curve=curve, interrupt=interrupt, **kwargs)



    def intersects(self, traverse_target=scene, ignore=(), debug=False):
        if isinstance(self.collider, MeshCollider):
            raise Exception('''error: mesh colliders can't intersect other shapes, only primitive shapes can. Mesh colliders can "receive" collisions though.''')

        from ursina.hit_info import HitInfo

        if not self.collision or not self.collider:
            self.hit = HitInfo(hit=False)
            return self.hit

        from ursina import distance
        if not hasattr(self, '_picker'):
            from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue
            from panda3d.core import CollisionRay, CollisionSegment, CollisionBox

            self._picker = CollisionTraverser()  # Make a traverser
            self._pq = CollisionHandlerQueue()  # Make a handler
            self._pickerNode = CollisionNode('raycaster')
            self._pickerNode.set_into_collide_mask(0)
            self._pickerNP = self.attach_new_node(self._pickerNode)
            self._picker.addCollider(self._pickerNP, self._pq)
            self._pickerNP.show()
            self._pickerNode.addSolid(self._collider.shape)

        if debug:
            self._pickerNP.show()
        else:
            self._pickerNP.hide()

        self._picker.traverse(traverse_target)

        if self._pq.get_num_entries() == 0:
            self.hit = HitInfo(hit=False)
            return self.hit

        ignore += (self, )
        ignore += tuple(e for e in scene.entities if not e.collision)

        self._pq.sort_entries()
        self.entries = [        # filter out ignored entities
            e for e in self._pq.getEntries()
            if e.get_into_node_path().parent not in ignore
            ]

        if len(self.entries) == 0:
            self.hit = HitInfo(hit=False, distance=0)
            return self.hit

        collision = self.entries[0]
        nP = collision.get_into_node_path().parent
        point = collision.get_surface_point(nP)
        point = Vec3(*point)
        world_point = collision.get_surface_point(render)
        world_point = Vec3(*world_point)
        hit_dist = distance(self.world_position, world_point)

        self.hit = HitInfo(hit=True)
        self.hit.entity = next(e for e in scene.entities if e == nP)

        self.hit.point = point
        self.hit.world_point = world_point
        self.hit.distance = hit_dist

        normal = collision.get_surface_normal(collision.get_into_node_path().parent).normalized()
        self.hit.normal = Vec3(*normal)

        normal = collision.get_surface_normal(render).normalized()
        self.hit.world_normal = Vec3(*normal)

        self.hit.entities = []
        for collision in self.entries:
            self.hit.entities.append(next(e for e in scene.entities if e == collision.get_into_node_path().parent))

        return self.hit



if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='quad', color=color.orange, position=(0,0,1), scale=1.5, rotation=(0,0,45), texture='brick')

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


    # test
    e = Entity(model='cube')
    # e.animate_x(3, duration=2, delay=.5, loop=True)
    # e.animate_position(Vec3(1,1,1), duration=1, loop=True)
    # e.animate_rotation(Vec3(45,45,45))
    # e.animate_scale(2, duration=1, curve=curve.out_expo_boomerang, loop=True)
    # e.animate_color(color.green, loop=True)
    # e.shake()
    # e.fade_out(delay=.5)
    # e.fade_in(delay=2.5)
    e.blink(color.red, duration=1, curve=curve.linear_boomerang, loop=True)



    app.run()
