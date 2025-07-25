import ursina
import builtins
from typing import Literal
from pathlib import Path
from panda3d.core import NodePath
from ursina.vec2 import Vec2
from ursina.vec3 import Vec3
from ursina.vec4 import Vec4
from panda3d.core import Quat
from panda3d.core import TransparencyAttrib
from panda3d.core import TexGenAttrib

from ursina.texture import Texture
from panda3d.core import MovieTexture
from panda3d.core import TextureStage
from panda3d.core import CullFaceAttrib

from ursina import application
from ursina.collider import Collider, BoxCollider, SphereCollider, MeshCollider, CapsuleCollider
from ursina.mesh import Mesh, MeshModes
from ursina.sequence import Sequence, Func, Wait
from ursina.ursinamath import lerp
from ursina import curve
from ursina.mesh_importer import load_model
from ursina.texture_importer import load_texture
from ursina.string_utilities import camel_to_snake
from textwrap import dedent
from panda3d.core import Shader as Panda3dShader
from ursina import shader
from ursina.shader import Shader
from ursina.string_utilities import print_warning
from ursina.ursinamath import Bounds
from ursina.ursinastuff import invoke, PostInitCaller, after, Default

from ursina import color
from ursina.color import Color
from ursina.shaders.unlit_shader import unlit_shader
try:
    from ursina.scene import instance as scene
except:
    pass

_Ursina_instance = None
_warn_if_ursina_not_instantiated = True # gets set to True after Ursina.__init__() to ensure the correct order.


from ursina.scripts.property_generator import generate_properties_for_class
@generate_properties_for_class()
class Entity(NodePath, metaclass=PostInitCaller):
    rotation_directions = (-1,-1,1)
    default_shader = unlit_shader
    default_values = {
        'parent':scene,
        'name':'entity', 'enabled':True, 'eternal':False, 'position':Vec3(0,0,0), 'rotation':Vec3(0,0,0), 'scale':Vec3(1,1,1), 'model':None, 'origin':Vec3(0,0,0),
        'shader':'unlit_shader', 'texture':None, 'texture_scale':Vec2(1,1), 'color':color.white, 'collider':None}

    def __init__(self,
        add_to_scene_entities=True,
        enabled=True,
        parent=scene,
        position=Vec3(0,0,0),
        rotation=Vec3(0,0,0),
        scale=Vec3(1,1,1),
        model='',
        origin=Vec3(0,0,0),
        shader=Default,
        color=color.white,
        texture='',
        texture_scale=Vec2.one,
        texture_offset=Vec2.zero,
        collider=None,
        eternal=False,
    #     # name='entity',
        **kwargs
        ):
        self._children = []
        super().__init__(self.__class__.__name__)

        self.name = camel_to_snake(self.__class__.__name__)
        self.ignore = False     # if True, will not try to run code.
        self.ignore_paused = False      # if True, will still run when application is paused. useful when making a pause menu for example.
        self.ignore_input = False
        self.add_to_scene_entities = add_to_scene_entities # set to False to be ignored by the engine, but still get rendered.

        self._shader_inputs = {}
        self.setPythonTag('Entity', self)   # for the raycast to get the Entity and not just the NodePath
        self.scripts = []   # add with add_script(class_instance). will assign an 'entity' variable to the script.
        self.animations = []
        self.hovered = False    # will return True if mouse hovers entity.

        self.parent = parent     # default parent is scene, which means it's in 3d space. to use UI space, set the parent to camera.ui instead.
        self.position = position
        self.rotation = rotation
        self.scale = scale

        self.shader = shader if shader is not Default else __class__.default_shader
        self.model = model
        if origin != __class__.default_values['origin']: self.origin = origin
        for key in ('origin_x', 'origin_y', 'origin_z'):
            if key in kwargs:
                setattr(self, key, kwargs[key])
                del kwargs[key]

        if color != __class__.default_values['color']: self.color = color
        self.texture = texture
        self.texture_scale = texture_scale
        self.texture_offset = texture_offset
        self.enabled = enabled
        self.eternal = eternal
        self.collider = collider

        for key, value in kwargs.items():
            setattr(self, key, value)


        # look for @every decorator and start a looping Sequence for decorated method
        from ursina.scripts.every_decorator import every, get_class_name
        for method in every.decorated_methods:
            if get_class_name(method._func) == self.types[0]:
                self.animations.append(Sequence(Func(method, self), Wait(method._every.interval), loop=True, started=True, entity=self))
                print('append to animations:', self)


        self.line_definition = None # returns a Traceback(filename, lineno, function, code_context, index).
        if application.trace_entity_definition and add_to_scene_entities or (not _Ursina_instance and _warn_if_ursina_not_instantiated and add_to_scene_entities):
            from inspect import getframeinfo, stack
            _stack = stack()
            caller = getframeinfo(_stack[1][0])
            if len(_stack) > 2 and _stack[1].code_context and 'super().__init__()' in _stack[1].code_context[0]:
                caller = getframeinfo(_stack[3][0])

            self.line_definition = caller
            if caller.code_context:
                self.code_context = caller.code_context[0]

                if (self.code_context.count('(') == self.code_context.count(')') and
                ' = ' in self.code_context and 'name=' not in self.code_context
                and 'Ursina()' not in self.code_context):

                    self.name = self.code_context.split(' = ')[0].strip().replace('self.', '')
                    # print('set name to:', self.code_context.split(' = ')[0].strip().replace('self.', ''))

                if application.print_entity_definition:
                    print(f'{Path(caller.filename).name} ->  {caller.lineno} -> {caller.code_context}')

        if not _Ursina_instance and _warn_if_ursina_not_instantiated and add_to_scene_entities:
            print_warning('Tried to instantiate Entity before Ursina. Please create an instance of Ursina first (app = Ursina())', self.line_definition)



    def __post_init__(self):
        if self.add_to_scene_entities:
            scene.entities.append(self)

        if self.enabled and hasattr(self, 'on_enable'):
            self.on_enable()

        elif not self.enabled and hasattr(self, 'on_disable'):
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


    def enable(self): # same as .enabled = True
        self.enabled = True

    def disable(self): # same as .enabled = False
        self.enabled = False


    def enabled_getter(self):
        return getattr(self, '_enabled', True)

    def enabled_setter(self, value):    # disabled entities will not be visible nor run code.
        original_value = self.enabled
        self._enabled = value

        if value and not original_value and hasattr(self, 'on_enable'):
            self.on_enable()

        if not value and original_value and hasattr(self, 'on_disable'):
            self.on_disable()

        if value:
            if hasattr(self, 'is_singleton') and not self.is_singleton():
                self.unstash()
        else:
            if hasattr(self, 'is_singleton') and not self.is_singleton():
                self.stash()

        for loose_child in self.loose_children:
            loose_child.enabled = value



    def model_setter(self, value):  # set model with model='model_name' (without file type extension)
        if value == '':
            value = None
        if value is None:
            if self.model:
                self.model.removeNode()
                # print('removed model')
            self._model = value
            return

        # if isinstance(value, Mesh) and value.mode == MeshModes.point:
        #     from ursina.shaders.point_shader import point_shader
        #     self.shader = point_shader
        #     self.set_shader_input('render_points_in_3d', value.render_points_in_3d)
        #     self.set_shader_input('thickness', value.thickness)


        if isinstance(value, NodePath): # pass procedural model
            if self.model and value != self.model:
                self.model.detachNode()
            self._model = value

        elif isinstance(value, str): # pass model asset name
            m = load_model(value)
            if not m:
                if application.raise_exception_on_missing_model:
                    raise ValueError(f"missing model: '{value}'")

                print_warning(f"missing model: '{value}'")
                return

            if self.model is not None:
                self.model.removeNode()

            m.name = value
            m.setPos(Vec3(0,0,0))
            self._model = m


        if self._model:
            self._model.reparentTo(self)
            self._model.setTransparency(TransparencyAttrib.M_dual)
            self.color = self.color # reapply color after changing model
            self.texture = self.texture # reapply texture after changing model
            self._vert_cache = None
            if isinstance(value, Mesh):
                if hasattr(value, 'on_assign'):
                    value.on_assign(assigned_to=self)


    def color_getter(self):
        return getattr(self, '_color', color.white)

    def color_setter(self, value):  # example: Entity(model='cube', color=hsv(30,1,.5))
        if isinstance(value, str):
            value = color.hex(value)

        if not isinstance(value, Vec4):
            value = Vec4(value[0], value[1], value[2], value[3])

        self._color = value

        if self.model:
            # print('SET COLOR TO', value, self.name)
            self.model.setColorScaleOff() # prevent inheriting color from parent
            self.model.setColorScale(value)


    def eternal_getter(self):
        return getattr(self, '_eternal', False)

    def eternal_setter(self, value):    # eternal entities does not get destroyed on scene.clear()
        self._eternal = value
        for c in self.children + self.loose_children:
            c.eternal = value

    def _ensure_is_not_destroyed(self):
        if not application.development_mode:
            return
        if self.is_empty():
            raise Exception(f'entity has been destroyed by: {self.destroy_source}')


    def double_sided_setter(self, value):
        self._double_sided = value
        self.setTwoSided(value)


    def render_queue_getter(self):
        return getattr(self, '_render_queue', 0)

    def render_queue_setter(self, value):   # for custom sorting in case of conflict. To sort things in 2d, set .z instead of using this.
        self._render_queue = value
        if self.model:
            self.model.setBin('fixed', value)


    def parent_setter(self, value):
        if hasattr(self, '_parent') and self._parent and hasattr(self._parent, '_children') and self in self._parent._children:
            self._parent._children.remove(self)

        if hasattr(value, '_children') and self not in value._children:
            value._children.append(self)

        self._parent = value
        if value is None:
            self.enabled = False
            return
        #     value = scene
        self.reparent_to(value)
        self.enabled = self.enabled   # parenting will undo the .stash() done when setting .enabled to False, so reapply it here


    def loose_parent_getter(self):
        return getattr(self, '_loose_parent', None)

    def loose_parent_setter(self, value):
        if hasattr(self, '_loose_parent') and self._loose_parent and hasattr(self._loose_parent, '_loose_children') and self in self._loose_parent._loose_children:
            self._loose_parent._loose_children.remove(self)

        if not hasattr(value, '_loose_children'):
            value.loose_children = []
        value._loose_children.append(self)

        self._loose_parent = value


    def world_parent_getter(self):
        return getattr(self, '_parent', None)

    def world_parent_setter(self, value):  # change the parent, but keep position, rotation and scale
        if hasattr(self, '_parent') and self._parent and hasattr(self._parent, '_children') and self in self._parent._children:
            self._parent._children.remove(self)

        if hasattr(value, '_children') and self not in value._children:
            value._children.append(self)

        self.wrtReparentTo(value)
        self.enabled = self._enabled   # parenting will undo the .stash() done when setting .enabled to False, so reapply it here
        self._parent = value


    @property
    def types(self): # get all class names including those this inherits from.
        from inspect import getmro
        return [c.__name__ for c in getmro(self.__class__)]


    def visible_getter(self):
        return getattr(self, '_visible', True)

    def visible_setter(self, value):
        self._visible = value
        if value:
            self.show()
        else:
            self.hide()

    def visible_self_getter(self): # set visibility of self, without affecting children.
        return getattr(self, '_visible_self', True)

    def visible_self_setter(self, value):
        self._visible_self = value
        if not self.model:
            return
        if value:
            self.model.show()
        else:
            self.model.hide()


    def collider_getter(self):
        return getattr(self, '_collider', None)

    def collider_setter(self, value: Collider | Literal['box','sphere','capsule','mesh']):   # set to 'box'/'sphere'/'capsule'/'mesh' for auto fitted collider.
        if value is None and self.collider:
            self._collider.remove()
            self._collider = None
            self.collision = False
            return

        # destroy existing collider
        if value and self.collider:
            self._collider.remove()

        if isinstance(value, Collider):
            self._collider = value

        if isinstance(value, str) and value not in ('box', 'sphere', 'capsule', 'mesh'):
            raise ValueError(f"Incorrect value for auto-fitted collider: {value}. Choose one of: 'box', 'sphere', 'capsule', 'mesh'")

        elif value == 'box':
            if self.model:
                _bounds = self.model_bounds
                self._collider = BoxCollider(entity=self, center=_bounds.center, size=_bounds.size)
            else:
                self._collider = BoxCollider(entity=self)
            self._collider.name = value

        elif value == 'sphere':
            self._collider = SphereCollider(entity=self, center=-self.origin)
            self._collider.name = value

        elif value == 'capsule':
            self._collider = CapsuleCollider(entity=self, center=-self.origin)
            self._collider.name = value

        elif value == 'mesh' and self.model:
            self._collider = MeshCollider(entity=self, mesh=self.model, center=-self.origin)
            self._collider.name = value

        elif isinstance(value, Mesh):
            self._collider = MeshCollider(entity=self, mesh=value, center=-self.origin)

        elif isinstance(value, str):
            m = load_model(value)
            if not m:
                self._collider = None
                self._collision = False
                return
            self._collider = MeshCollider(entity=self, mesh=m, center=-self.origin)
            self._collider.name = value


        self.collision = bool(self.collider)
        return

    def collision_getter(self):
        return getattr(self, '_collision', False)

    def collision_setter(self, value):  # toggle collision without changing collider.
        self._collision = value
        if not hasattr(self, 'collider') or not self.collider:
            if self in scene.collidables:
                scene.collidables.remove(self)
            return

        if value:
            self.collider.node_path.unstash()
            scene.collidables.add(self)
        else:
            self.collider.node_path.stash()
            if self in scene.collidables:
                scene.collidables.remove(self)


    def on_click_getter(self):
        return getattr(self, '_on_click', None)

    def on_click_setter(self, value):
        '''
        def action():
            print('Ow! That hurt!')

        Entity(model='quad', parent=camera.ui, scale=.1, collider='box', on_click=action)
        '''
        if not callable(value):
            raise TypeError(f'on_click must be a callabe, not {type(value)}')
        self._on_click = value


    def origin_getter(self):
        return getattr(self, '_origin', Vec3.zero)

    def origin_setter(self, value):
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.origin_z)

        self._origin = value

        if self.model:
            self.model.setPos(-value[0], -value[1], -value[2])


    def origin_x_getter(self):
        return self.origin[0]
    def origin_x_setter(self, value):   # Convenience property for setting first element of origin
        self.origin = Vec3(value, self.origin_y, self.origin_z)

    def origin_y_getter(self):
        return self.origin[1]
    def origin_y_setter(self, value): # Convenience property for setting second element of origin. Example: Entity(model='cube', origin_y=-.5) # The origin point of the cube is now at the bottom instead of the center.
        self.origin = Vec3(self.origin_x, value, self.origin_z)

    def origin_z_getter(self):
        return self.origin[2]
    def origin_z_setter(self, value):   # Convenience property for setting second element of origin
        self.origin = Vec3(self.origin_x, self.origin_y, value)

    def world_position_getter(self):
        self._ensure_is_not_destroyed()
        return Vec3(self.get_position(scene))

    def world_position_setter(self, value):
        self._ensure_is_not_destroyed()
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.z)

        self.setPos(scene, Vec3(value[0], value[1], value[2]))

    def world_x_getter(self):
        self._ensure_is_not_destroyed()
        return self.getX(scene)
    def world_y_getter(self):
        self._ensure_is_not_destroyed()
        return self.getY(scene)
    def world_z_getter(self):
        self._ensure_is_not_destroyed()
        return self.getZ(scene)

    def world_x_setter(self, value):
        self._ensure_is_not_destroyed()
        self.setX(scene, value)
    def world_y_setter(self, value):
        self._ensure_is_not_destroyed()
        self.setY(scene, value)
    def world_z_setter(self, value):
        self._ensure_is_not_destroyed()
        self.setZ(scene, value)

    def position_getter(self):
        self._ensure_is_not_destroyed()
        return Vec3(*self.getPos())

    def position_setter(self, value):   # right, up, forward. can also set self.x, self.y, self.z
        self._ensure_is_not_destroyed()
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.z)

        self.setPos(value[0], value[1], value[2])

    def x_getter(self):
        self._ensure_is_not_destroyed()
        return self.getX()
    def x_setter(self, value):
        self._ensure_is_not_destroyed()
        self.setX(value)

    def y_getter(self):
        self._ensure_is_not_destroyed()
        return self.getY()
    def y_setter(self, value):
        self._ensure_is_not_destroyed()
        self.setY(value)

    def z_getter(self):
        self._ensure_is_not_destroyed()
        return self.getZ()
    def z_setter(self, value):
        self._ensure_is_not_destroyed()
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

    def world_rotation_getter(self):
        self._ensure_is_not_destroyed()
        rotation = self.getHpr(scene)
        return Vec3(rotation[1], rotation[0], rotation[2]) * Entity.rotation_directions

    def world_rotation_setter(self, value):
        self._ensure_is_not_destroyed()
        self.setHpr(scene, Vec3(value[1], value[0], value[2]) * Entity.rotation_directions)

    def world_rotation_x_getter(self):
        self._ensure_is_not_destroyed()
        return self.world_rotation[0]

    def world_rotation_x_setter(self, value):
        self._ensure_is_not_destroyed()
        self.world_rotation = Vec3(value, self.world_rotation[1], self.world_rotation[2])

    def world_rotation_y_getter(self):
        self._ensure_is_not_destroyed()
        return self.world_rotation[1]

    def world_rotation_y_setter(self, value):
        self._ensure_is_not_destroyed()
        self.world_rotation = Vec3(self.world_rotation[0], value, self.world_rotation[2])

    def world_rotation_z_getter(self):
        self._ensure_is_not_destroyed()
        return self.world_rotation[2]

    def world_rotation_z_setter(self, value):
        self._ensure_is_not_destroyed()
        self.world_rotation = Vec3(self.world_rotation[0], self.world_rotation[1], value)

    def rotation_getter(self):
        self._ensure_is_not_destroyed()
        rotation = self.getHpr()
        return Vec3(rotation[1], rotation[0], rotation[2]) * Entity.rotation_directions

    def rotation_setter(self, value):   # can also set self.rotation_x, self.rotation_y, self.rotation_z
        self._ensure_is_not_destroyed()
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.rotation_z)

        self.setHpr(Vec3(value[1], value[0], value[2]) * Entity.rotation_directions)

    def rotation_x_getter(self):
        self._ensure_is_not_destroyed()
        return self.rotation.x
    def rotation_x_setter(self, value):
        self._ensure_is_not_destroyed()
        self.rotation = Vec3(value, self.rotation[1], self.rotation[2])

    def rotation_y_getter(self):
        self._ensure_is_not_destroyed()
        return self.rotation.y
    def rotation_y_setter(self, value):
        self._ensure_is_not_destroyed()
        self.rotation = Vec3(self.rotation[0], value, self.rotation[2])

    def rotation_z_getter(self):
        self._ensure_is_not_destroyed()
        return self.rotation.z
    def rotation_z_setter(self, value):
        self._ensure_is_not_destroyed()
        self.rotation = Vec3(self.rotation[0], self.rotation[1], value)

    def quaternion_getter(self):
        self._ensure_is_not_destroyed()
        return self.get_quat()
    def quaternion_setter(self, value):
        self._ensure_is_not_destroyed()
        self.set_quat(value)

    def world_scale_getter(self):
        self._ensure_is_not_destroyed()
        return Vec3(*self.getScale(scene))
    def world_scale_setter(self, value):
        self._ensure_is_not_destroyed()
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)

        if isinstance(value, Vec2):
            value = Vec3(*value, self.scale_z)

        value = Vec3(*[e if e!=0 else .001 for e in value])
        self.setScale(scene, value)

    def world_scale_x_getter(self):
        self._ensure_is_not_destroyed()
        return self.getScale(scene)[0]
    def world_scale_x_setter(self, value):
        self._ensure_is_not_destroyed()
        value = value if value != 0 else .001 # prevent panda3d erroring when scale is 0
        self.setScale(scene, Vec3(value, self.world_scale_y, self.world_scale_z))

    def world_scale_y_getter(self):
        self._ensure_is_not_destroyed()
        return self.getScale(scene)[1]
    def world_scale_y_setter(self, value):
        self._ensure_is_not_destroyed()
        value = value if value != 0 else .001 # prevent panda3d erroring when scale is 0
        self.setScale(scene, Vec3(self.world_scale_x, value, self.world_scale_z))

    def world_scale_z_getter(self):
        self._ensure_is_not_destroyed()
        return self.getScale(scene)[2]
    def world_scale_z_setter(self, value):
        self._ensure_is_not_destroyed()
        value = value if value != 0 else .001 # prevent panda3d erroring when scale is 0
        self.setScale(scene, Vec3(self.world_scale_x, self.world_scale_y, value))

    def scale_getter(self):
        self._ensure_is_not_destroyed()
        scale = self.getScale()
        return Vec3(scale[0], scale[1], scale[2])

    def scale_setter(self, value):  # can also set self.scale_x, self.scale_y, self.scale_z
        self._ensure_is_not_destroyed()
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.scale_z)

        value = [e if e!=0 else .001 for e in value]
        self.setScale(value[0], value[1], value[2])

    def scale_x_getter(self):
        self._ensure_is_not_destroyed()
        return self.scale[0]
    def scale_x_setter(self, value):
        self._ensure_is_not_destroyed()
        value = value if value != 0 else .001 # prevent panda3d erroring when scale is 0
        self.setScale(value, self.scale_y, self.scale_z)

    def scale_y_getter(self):
        self._ensure_is_not_destroyed()
        return self.scale[1]
    def scale_y_setter(self, value):
        self._ensure_is_not_destroyed()
        value = value if value != 0 else .001 # prevent panda3d erroring when scale is 0
        self.setScale(self.scale_x, value, self.scale_z)

    def scale_z_getter(self):
        self._ensure_is_not_destroyed()
        return self.scale[2]
    def scale_z_setter(self, value):
        self._ensure_is_not_destroyed()
        value = value if value != 0 else .001 # prevent panda3d erroring when scale is 0
        self.setScale(self.scale_x, self.scale_y, value)

    def transform_getter(self): # get/set position, rotation and scale
        self._ensure_is_not_destroyed()
        return (self.position, self.rotation, self.scale)
    def transform_setter(self, value):
        self._ensure_is_not_destroyed()
        self.position, self.rotation, self.scale = value

    def world_transform_getter(self): # get/set world_position, world_rotation and world_scale
        self._ensure_is_not_destroyed()
        return (self.world_position, self.world_rotation, self.world_scale)
    def world_transform_setter(self, value):
        self._ensure_is_not_destroyed()
        self.world_position, self.world_rotation, self.world_scale = value


    @property
    def forward(self): # get forward direction.
        return Vec3(*scene.getRelativeVector(self, (0, 0, 1)))
    @property
    def back(self): # get backwards direction.
        return -self.forward
    @property
    def right(self): # get right direction.
        return Vec3(*scene.getRelativeVector(self, (1, 0, 0)))
    @property
    def left(self): # get left direction.
        return -self.right
    @property
    def up(self): # get up direction.
        return Vec3(*scene.getRelativeVector(self, (0, 1, 0)))
    @property
    def down(self): # get down direction.
        return -self.up

    @property
    def screen_position(self): # get screen position(ui space) from world space.
        from ursina import camera
        world_pos = camera.getRelativePoint(self, Vec3.zero)
        projected_pos = camera.lens.getProjectionMat().xform(Vec4(*world_pos, 1))
        reciprocal_w = 1 / projected_pos[3] if projected_pos[3] > 0 else 1
        normalized_pos = projected_pos * reciprocal_w
        return Vec2(normalized_pos[0] * camera.aspect_ratio / 2, normalized_pos[1] / 2)

    # def shader_getter(self):
    #     return self._shader

    def shader_setter(self, value):

        # if not self.model:
        #     return

        # if value is None:
        #     self.setShaderAuto()
        #     return
        # # test
        # if value == Entity.default_shader:
        #     self.setShaderAuto()
        #     return

        if value is None and self.name != 'camera':
            self._shader = value
            return

        if isinstance(value, Panda3dShader): # panda3d shader
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


    def get_shader_input(self, name):
        return self._shader_inputs.get(name, None)

    def set_shader_input(self, name, value):
        self._shader_inputs[name] = value
        if isinstance(value, str):
            value = load_texture(value)

        if isinstance(value, Texture):
            value = value._texture    # make sure to send the panda3d texture to the shader

        try:
            super().set_shader_input(name, value)
        except:
            raise Exception(f'Incorrect input to shader: {name} {value}')

    def shader_input_getter(self):
        return self._shader_inputs

    def shader_input_setter(self, value):
        for key, value in value.items():
            self.set_shader_input(key, value)


    def material_setter(self, value):  # a way to set shader, texture, texture_scale, texture_offset and shader inputs in one go
        if value is None:
            raise ValueError('material can not be set to None')
        _shader = value.get('shader', None)
        if _shader is not None:
            self.shader = _shader

        for name in ('texture', 'texture_scale', 'texture_offset', 'color'):
            if name in value:
                setattr(self, name, value[name])

        if self.shader is not None:
            self.shader_input = {key: value for key, value in value.items() if key in _shader.default_input}


    def texture_setter(self, value):    # set model with texture='texture_name'. requires a model to be set beforehand.
        if not value:
            # print('remove texture')
            self._texture = value
            if self.model:
                self.model.clearTexture()
            return

        if isinstance(value, str):
            texture_name = value
            value = load_texture(value)
            # print('loaded texture:', texture)
            if value is None:
                if application.raise_exception_on_missing_texture:
                    raise ValueError(f"missing texture: '{texture_name}'")

                print_warning(f"missing texture: '{texture_name}'")
                return

        if self.model:
            self.model.setTextureOff(False)

        if value.__class__ is MovieTexture:
            self._texture = value
            if self.model:
                self.model.setTexture(value, 1)
            return

        self._texture = value
        if self.model and value is not None:
            self.model.setTexture(value._texture, 1)


    def texture_scale_getter(self):
        if 'texture_scale' in self._shader_inputs:
            return self._shader_inputs['texture_scale']
        else:
            return Vec2(1,1)

    def texture_scale_setter(self, value):  # how many times the texture should repeat, eg. texture_scale=(8,8).
        value = Vec2(*value)
        if self.model and self.texture:
            self.model.setTexScale(TextureStage.getDefault(), value[0], value[1])
            self.set_shader_input('texture_scale', value)

    def texture_offset_getter(self):
        return getattr(self, '_texture_offset', Vec2(0,0))

    def texture_offset_setter(self, value):
        value = Vec2(*value)
        if self.model and self.texture:
            self.model.setTexOffset(TextureStage.getDefault(), value[0], value[1])
            self.texture = self.texture
            self.set_shader_input('texture_offset', value)
        self._texture_offset = value

    def tileset_size_getter(self):         # if the texture is a tileset, say how many tiles there are so it only use one tile of the texture, e.g. tileset_size=[8,4]
        return getattr(self, '_tileset_size', Vec2.one)
    def tileset_size_setter(self, value):
        self._tileset_size = value
        self.texture_scale = Vec2(1/value[0], 1/value[1])

    def tile_coordinate_getter(self):      # set the tile coordinate, starts in the lower left.
        return self._tile_coordinate
    def tile_coordinate_setter(self, value):
        self._tile_coordinate = value
        self.texture_offset = Vec2(value[0] / self.tileset_size[0], value[1] / self.tileset_size[1])


    def alpha_getter(self):
        return self.color[3]

    def alpha_setter(self, value):  # shortcut for setting color's transparency/opacity
        if value > 1:
            value = value / 255
        self.color = color.hsv(self.color.h, self.color.s, self.color.v, value)


    def always_on_top_setter(self, value):
        self._always_on_top = value
        self.set_bin("fixed", 0)
        self.set_depth_write(not value)
        self.set_depth_test(not value)


    def unlit_setter(self, value):  # set to True to ignore light and not cast shadows
        self._unlit = value
        self.setLightOff(value)
        if value:
            self.hide(0b0001)
        else:
            self.show(0b0001)


    def billboard_setter(self, value):  # set to True to make this Entity always face the camera.
        self._billboard = value
        if value:
            self.setBillboardPointEye(value)


    def wireframe_setter(self, value):  # set to True to render model as wireframe
        self._wireframe = value
        self.setRenderModeWireframe(value)


    # def generate_sphere_map(self, size=512, name=f'sphere_map_{len(scene.entities)}'):
    #     from ursina import camera
    #     _name = 'textures/' + name + '.jpg'
    #     org_pos = camera.position
    #     camera.position = self.position
    #     application.base.saveSphereMap(_name, size=size)
    #     camera.position = org_pos

    #     # print('saved sphere map:', name)
    #     self.model.setTexGen(TextureStage.getDefault(), TexGenAttrib.MEyeSphereMap)
    #     self.reflection_map = name


    # def generate_cube_map(self, size=512, name=f'cube_map_{len(scene.entities)}'):
    #     from ursina import camera
    #     _name = 'textures/' + name
    #     org_pos = camera.position
    #     camera.position = self.position
    #     application.base.saveCubeMap(_name+'.jpg', size=size)
    #     camera.position = org_pos

    #     # print('saved cube map:', name + '.jpg')
    #     self.model.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldCubeMap)
    #     self.reflection_map = _name + '#.jpg'
    #     self.model.setTexture(builtins.loader.loadCubeMap(_name + '#.jpg'), 1)


    @property
    def model_bounds(self):
        if self.model:
            if not self.model.getTightBounds():
                return Bounds(center=Vec3.zero, size=Vec3.zero)

            start, end = self.model.getTightBounds()
            start = Vec3(start)
            end = Vec3(end)
            center = (start + end) / 2
            size = end - start
            return Bounds(center=center, size=size)

        return None


    @property
    def bounds(self):
        _bounds = self.model_bounds
        if _bounds is None:
            return None
        return Bounds(center=_bounds.center, size=_bounds.size*self.scale)


    def get_position(self, relative_to=scene):  # get position relative to on other Entity. In most cases, use .position instead.
        return Vec3(*self.getPos(relative_to))


    def set_position(self, value, relative_to=scene): # set position relative to on other Entity. In most cases, use .position instead.
        self.setPos(relative_to, Vec3(value[0], value[1], value[2]))


    def rotate(self, value, relative_to=None):  # rotate around local axis.
        if not relative_to:
            relative_to = self

        self.setHpr(relative_to, Vec3(value[1], value[0], value[2]) * Entity.rotation_directions)


    def add_script(self, class_instance):
        if isinstance(class_instance, object) and not isinstance(class_instance, str):
            class_instance.entity = self
            class_instance.enabled = True
            self.scripts.append(class_instance)
            if hasattr(class_instance, 'on_script_added') and callable(class_instance.on_script_added):
                class_instance.on_script_added()
            # print('added script:', camel_to_snake(name.__class__.__name__))
            return class_instance


    def combine(self, analyze=False, auto_destroy=True, ignore=[], ignore_disabled=True, include_normals=False):
        from ursina.scripts.combine import combine

        self.model = combine(self, analyze, auto_destroy, ignore, ignore_disabled, include_normals)
        return self.model


    def flipped_faces_setter(self, value):
        self._flipped_faces = value
        if value:
            self.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullClockwise))
        else:
            self.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))


    def look_at(self, target, axis=Vec3.forward):
        if isinstance(target, Entity):
            target = Vec3(*target.world_position)
        elif not isinstance(target, Vec3):
            target = Vec3(*target)

        if isinstance(axis, str):
            print_warning('look_at axis as str is deprecated, use one of: Vec3.forward/Vec3.back/Vec3.up/Vec3.down/Vec3.right/Vec3.left')
        if axis == 'forward':
            axis = Vec3.forward
        elif axis == 'back':
            axis = Vec3.back
        elif axis == 'up':
            axis = Vec3.up
        elif axis == 'down':
            axis = Vec3.down
        elif axis == 'right':
            axis = Vec3.right
        elif axis == 'left':
            axis = Vec3.left

        self.look_in_direction((target-self.world_position).normalized(), axis)


    def look_in_direction(self, direction, forward_axis=Vec3.forward):
        import math
        def normalize_vector(v):
            length = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
            if length == 0:
                return (0, 0, 0)
            return (v[0] / length, v[1] / length, v[2] / length)

        def dot_product(v1, v2):
            return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

        def cross_product(v1, v2):
            return (
                v1[1] * v2[2] - v1[2] * v2[1],
                v1[2] * v2[0] - v1[0] * v2[2],
                v1[0] * v2[1] - v1[1] * v2[0]
            )

        def quaternion_multiply(q1, q2):
            w1, x1, y1, z1 = q1
            w2, x2, y2, z2 = q2

            w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
            x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
            y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
            z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2

            return Quat(w, x, y, z)

        def rotate_vector_by_quaternion(vec, quat):
            vec_quat = Quat(0, vec[0], vec[1], vec[2])
            quat_conjugate = Quat(quat[0], -quat[1], -quat[2], -quat[3])
            vec_rotated = quaternion_multiply(quaternion_multiply(quat, vec_quat), quat_conjugate)  # Rotate the vector using quaternion multiplication
            return Vec3(vec_rotated[1], vec_rotated[2], vec_rotated[3])

        def align_vectors(v1, v2, forward):
            """Align v1 to v2 around the forward axis by computing the roll quaternion."""
            # Compute the axis perpendicular to both vectors
            axis = cross_product(v1, v2)

            axis = normalize_vector(axis)

            # Compute the angle between the vectors
            cos_angle = dot_product(v1, v2)
            cos_angle = max(min(cos_angle, 1.0), -1.0)  # Clamp to avoid math errors
            angle = math.acos(cos_angle)

            # Create a quaternion that rotates around the forward axis
            half_angle = angle / 2
            sin_half_angle = math.sin(half_angle)

            roll_quaternion = (math.cos(half_angle), forward[0]*sin_half_angle, forward[1]*sin_half_angle, forward[2]*sin_half_angle)
            return roll_quaternion

        def quaternion_from_axis_and_angle(axis, angle):
            half_angle = angle / 2
            sin_half_angle = math.sin(half_angle)
            return (math.cos(half_angle), axis[0]*sin_half_angle, axis[1]*sin_half_angle, axis[2]*sin_half_angle)

        """
        Create a quaternion that aligns the specified forward_axis with the direction vector
        while maintaining the orientation of other axes as defined by previous_rotation.

        :param direction: The target direction to look in.
        :param forward_axis: The axis of the entity to align with the direction.
        :param previous_rotation: The quaternion representing the previous rotation.
        :return: A quaternion that represents the new rotation.
        """
        previous_rotation = self.quaternion
        # Normalize inputs
        direction = normalize_vector(direction)
        forward_axis = normalize_vector(forward_axis)

        # Check for near-zero direction to avoid invalid rotations
        if all(v == 0 for v in direction):
            return previous_rotation  # No rotation if direction is zero

        # Step 1: Calculate the target forward direction based on previous rotation
        current_forward = rotate_vector_by_quaternion(forward_axis, previous_rotation)

        dot_prod = dot_product(current_forward, direction)

        # Handle the edge case of 180-degree rotation
        if dot_prod < -0.9999:  # Vectors are nearly opposite
            # Choose an arbitrary axis to rotate around (perpendicular to forward_axis)
            # In this case, we need to rotate by 180 degrees
            arbitrary_axis = (1, 0, 0) if abs(dot_product(forward_axis, (1, 0, 0))) < 0.9999 else (0, 1, 0)
            sin_half_angle = math.sin(math.pi / 2)
            rotation_quat = (
                0,  # cos(180° / 2) = 0
                arbitrary_axis[0] * sin_half_angle,
                arbitrary_axis[1] * sin_half_angle,
                arbitrary_axis[2] * sin_half_angle
            )
        else:
            # Step 2: Find the rotation needed to align current_forward to the target direction
            rotation_axis = normalize_vector(cross_product(current_forward, direction))
            rotation_angle = math.acos(max(min(dot_product(current_forward, direction), 1.0), -1.0))

            # Step 3: Create a quaternion for this rotation
            sin_half_angle = math.sin(rotation_angle / 2)
            rotation_quat = Quat(
                math.cos(rotation_angle / 2),
                rotation_axis[0] * sin_half_angle,
                rotation_axis[1] * sin_half_angle,
                rotation_axis[2] * sin_half_angle
                )

        # Step 4: Combine the new rotation with the previous rotation
        new_rotation = quaternion_multiply(rotation_quat, previous_rotation)
        self.quaternion = new_rotation.normalized()


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

    def look_at_xy(self, target):
        self.look_at_2d(target)
    def look_at_xz(self, target):
        self.look_at_2d(target, 'y')


    def has_ancestor(self, possible_ancestor):
        if self.parent == possible_ancestor:
            return True

        p = self
        if isinstance(possible_ancestor, Entity):
            for i in range(100):
                if p.parent:
                    if p.parent == possible_ancestor:
                        return True

                    p = p.parent

        return False

    def get_descendants(self, include_disabled=True):       # recursively get all descendants (children, grandchildren, and so on)
        descendants = []
        for child in self.children:
            if not include_disabled and not child.enabled:
                continue  # Skip disabled children if include_disabled is False
            descendants.append(child)
            descendants.extend(child.get_descendants(include_disabled))  # Recursive call
        return descendants


    def has_disabled_ancestor(self):
        p = self
        for i in range(100):
            if not p.parent:
                return False
            if not hasattr(p, 'parent') or not hasattr(p.parent, 'enabled'):
                return False

            p = p.parent

            if p.enabled is False:
                return True

        return False

    def children_getter(self):
        return [e for e in getattr(self, '_children', []) if e]     # make sure list doesn't contain destroyed entities

    def children_setter(self, value):
        self._children = value

    def loose_children_getter(self):
        return getattr(self, '_loose_children', [])


    @property
    def attributes(self): # attribute names. used by duplicate().
        return ('name', 'enabled', 'eternal', 'visible', 'parent',
            'origin', 'position', 'rotation', 'scale',
            'shader', 'model', 'color', 'texture', 'texture_scale', 'texture_offset',
            'render_queue', 'always_on_top', 'collider', 'collision', 'scripts')

    def __str__(self):
        try:
            return self.name
        except:
            return '*destroyed entity*'

    def get_changes(self, target_class=None): # returns a dict of all the changes
        if not target_class:
            target_class = self.__class__

        changes = dict()
        for key, value in target_class.default_values.items():
            attr = getattr(self, key)
            if attr == target_class.default_values[key]:
                continue

            if hasattr(attr, '__name__'):
                attr = attr.__name__
                changes[key] = attr
                continue

            if attr and hasattr(attr, 'name') and attr.name and isinstance(attr.name, str):
                attr = attr.name
                if '.' in attr:
                    attr = attr.split('.')[0]

            # print('attr changed:', key, 'from:', target_class.default_values[key], 'to:', attr)
            if key == 'color':
                if isinstance(attr, str):
                    if not attr.startswith('#'):
                        attr = f'color.{attr}'
                elif isinstance(attr, Color):
                    attr = f"'{color.rgb_to_hex(*attr)}'"

            elif isinstance(attr, str):
                attr = f"'{attr}'"

            if attr == "'mesh'":
                continue

            changes[key] = attr
        return changes



    def __repr__(self):
        changes = self.get_changes(self.__class__)

        if 'parent' in changes: # ignore parent since we can't really get it as a string. you could handle this yourself though.
            del changes['parent']

        return f'{self.__class__.__name__}(' +  ''.join(f'{key}={value}, ' for key, value in changes.items()) + ')'


    def __deepcopy__(self, memo):
        return eval(repr(self))


#------------
# ANIMATIONS
#------------

    def _getattr(self, name):
        return getattr(self, name)

    def _setattr(self, name, value):
        setattr(self, name, value)

    def animate(self, name, value, duration=.1, delay=0, curve=curve.in_expo, loop=False, resolution=None, interrupt='kill', time_step=None, unscaled=False, ignore_paused=None, auto_play=True, auto_destroy=True, getattr_function=None, setattr_function=None, lerp_function=lerp):
        if duration == 0 and delay == 0:
            setattr(self, name, value)
            return None

        if ignore_paused is None:   # if ignore_pause is not specified, inherit it from the entity
            ignore_paused = self.ignore_paused

        animator_name = name + '_animator'
        # print('start animating value:', name, animator_name )
        if interrupt and hasattr(self, animator_name):
            getattr(getattr(self, animator_name), interrupt)() # call kill() or finish() depending on what the interrupt value is.
            # print('interrupt', interrupt, animator_name)
        if hasattr(self, animator_name) and getattr(self, animator_name) in self.animations:
            self.animations.remove(getattr(self, animator_name))

        sequence = Sequence(loop=loop, time_step=time_step, auto_destroy=auto_destroy, unscaled=unscaled, ignore_paused=ignore_paused, name=name)
        sequence.append(Wait(delay))

        setattr(self, animator_name, sequence)
        self.animations.append(sequence)

        if not resolution:
            resolution = max(int(duration * 60), 1)

        # if no custom getattr and setattr functions are provided (for example  when using animate_shader_input), animate the entity's variable.
        if not getattr_function:
            getattr_function = self._getattr
        if not setattr_function:
            setattr_function = self._setattr

        for i in range(resolution+1):
            t = i / resolution
            t = curve(t)

            sequence.append(Wait(duration / resolution), regenerate=False)
            sequence.append(Func(setattr_function, name, lerp_function(getattr_function(name), value, t)), regenerate=False)

        sequence.generate()
        if auto_play:
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

        return self.animate('scale', value, duration=duration, **kwargs)


    def animate_shader_input(self, name, value, **kwargs):
        # instead of setting entity variables, set shader input
        return self.animate(name, value, getattr_function=self.get_shader_input, setattr_function=self.set_shader_input, **kwargs)


    # generate animation functions
    for e in ('x', 'y', 'z', 'rotation_x', 'rotation_y', 'rotation_z', 'scale_x', 'scale_y', 'scale_z'):
        exec(dedent(f'''
            def animate_{e}(self, value, duration=.1, delay=0, unscaled=False, **kwargs):
                return self.animate('{e}', value, duration=duration, delay=delay, unscaled=unscaled, **kwargs)
        '''))


    def shake(self, duration=.2, magnitude=1, speed=.05, direction=(1,1), delay=0, attr_name='position', interrupt='finish', unscaled=False, ignore_paused=True):
        import random

        if hasattr(self, 'shake_sequence') and self.shake_sequence:
            getattr(getattr(self, 'shake_sequence'), interrupt)()

        self.shake_sequence = Sequence(Wait(delay))
        original_position = getattr(self, attr_name)

        for i in range(int(duration / speed)):
            self.shake_sequence.append(Func(setattr, self, attr_name,
                Vec3(
                    original_position[0] + (random.uniform(-.1, .1) * magnitude * direction[0]),
                    original_position[1] + (random.uniform(-.1, .1) * magnitude * direction[1]),
                    original_position[2],
                )))
            self.shake_sequence.append(Wait(speed))
            self.shake_sequence.append(Func(setattr, self, attr_name, original_position))

        self.animations.append(self.shake_sequence)
        self.shake_sequence.unscaled = unscaled
        self.shake_sequence.ignore_paused = ignore_paused
        self.shake_sequence.start()
        return self.shake_sequence

    def animate_color(self, value, duration=.1, interrupt='finish', unscaled=False, **kwargs):
        return self.animate('color', value, duration, **kwargs)

    def fade_out(self, value=0, duration=.5, unscaled=False, **kwargs):
        return self.animate('color', Vec4(self.color[0], self.color[1], self.color[2], value), duration=duration, **kwargs)

    def fade_in(self, value=1, duration=.5, **kwargs):
        return self.animate('color', Vec4(self.color[0], self.color[1], self.color[2], value), duration=duration, **kwargs)

    def blink(self, color=ursina.color.white, shader=unlit_shader, duration=.1):
        if not getattr(self, 'org_shader', False):
            self.org_shader = self.shader
            self.org_texture = self.texture
            self.org_color = self.color

        self.shader = shader
        self.texture = None
        self.color = color

        @after(duration, entity=self)
        def _reset(self=self):
            self.shader = self.org_shader
            self.texture = self.org_texture
            self.color = self.org_color


        # return self.animate_color(value, duration=duration, delay=delay, curve=curve, interrupt=interrupt, **kwargs)



    def intersects(self, traverse_target=scene, ignore:list=None, debug=False):
        if not ignore:
            ignore = []
        ignore = list(ignore)

        if isinstance(self.collider, MeshCollider):
            raise Exception('''error: mesh colliders can't intersect other shapes, only primitive shapes can. Mesh colliders can "receive" collisions though.''')

        from ursina.hit_info import HitInfo

        if not self.collision or not self.collider:
            self.hit = HitInfo(hit=False)
            return self.hit

        from ursina import distance
        if not hasattr(self, '_picker'):
            from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue

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

        ignore.append(self)
        ignore.extend((e for e in scene.entities if not e.collision))

        self._pq.sort_entries()
        entries = self._pq.getEntries()
        entities = [e.get_into_node_path().parent for e in entries]

        entries = [        # filter out ignored entities
            e for i, e in enumerate(entries)
            if entities[i] in scene.collidables
            and entities[i] not in ignore
            ]

        if len(entries) == 0:
            return HitInfo(hit=False)

        hit_info = HitInfo(hit=True)
        hit_info.entities = [e.get_into_node_path().parent.getPythonTag('Entity') for e in entries]
        hit_info.entity = hit_info.entities[0]

        collision = entries[0]
        # nP = collision.get_into_node_path().parent
        hit_info.point = Vec3(*collision.get_surface_point(hit_info.entity))
        hit_info.world_point = Vec3(*collision.get_surface_point(scene))
        hit_info.distance = distance(self.world_position, hit_info.world_point)
        hit_info.normal = Vec3(*collision.get_surface_normal(collision.get_into_node_path().parent).normalized())
        hit_info.world_normal = Vec3(*collision.get_surface_normal(scene).normalized())

        return hit_info



if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    # e = Entity(model='quad', color=color.orange, position=(0,0,1), scale=1.5, rotation=(0,0,45), texture='brick')

    # '''example of inheriting Entity'''
    # class Player(Entity):
    #     def __init__(self, **kwargs):
    #         super().__init__()
    #         self.model='cube'
    #         self.color = color.red
    #         self.scale_y = 2

    #         for key, value in kwargs.items():
    #             setattr(self, key, value)

    #     # input and update functions gets automatically called by the engine
    #     def input(self, key):
    #         if key == 'space':
    #             # self.color = self.color.inverse()
    #             self.animate_x(2, duration=1)

    #     def update(self):
    #         self.x += held_keys['d'] * time.dt * 10
    #         self.x -= held_keys['a'] * time.dt * 10

    # player = Player(x=-1)


    # # test
    # e = Entity(model='cube', collider='box', texture='shore', texture_scale=Vec2(2), color=hsv(.3,1,.5))
    # print(repr(e))
    # # a = Entity()
    # # b = Entity(parent=a)


    # # e.animate_x(3, duration=2, delay=.5, loop=True)
    # # e.animate_position(Vec3(1,1,1), duration=1, loop=True)
    # # e.animate_rotation(Vec3(45,45,45))
    # # e.animate_scale(2, duration=1, curve=curve.out_expo_boomerang, loop=True)
    # # e.animate_color(color.green, loop=True)
    # # e.shake()
    # # e.fade_out(delay=.5)
    # # e.fade_in(delay=2.5)
    # # e.blink(color.red, duration=1, curve=curve.linear_boomerang, loop=True)


    # shader test
    from ursina.shaders import matcap_shader, lit_with_shadows_shader
    ground = Entity(model='plane', texture='grass', scale=10, shader=lit_with_shadows_shader)
    e = Entity(model='cube', y=1, texture='grass',
        # shader=unlit_shader
        )
    e1 = Entity(parent=e, model='cube', y=1, x=.5, shader=matcap_shader, texture='shore')
    e2 = Entity(parent=e1, model='cube', x=2, shader=lit_with_shadows_shader, texture='white_cube')
    DirectionalLight().look_at(Vec3(1,-1,.5))
    EditorCamera(rotation_x=15)

    # # test deepcopy
    # print_warning(repr(e1))
    # e1_copy = deepcopy(e1)


    app.run()
