"""
ursina/entity.py

This module defines the Entity class, which is the base class for all objects in the Ursina engine.
Entities can have models, textures, colors, shaders, and other properties. They can also have children,
colliders, and animations. This module also provides various utility functions for manipulating entities.

Dependencies:
- builtins
- pathlib.Path
- panda3d.core.NodePath
- panda3d.core.Quat
- panda3d.core.TransparencyAttrib
- panda3d.core.TexGenAttrib
- panda3d.core.MovieTexture
- panda3d.core.TextureStage
- panda3d.core.CullFaceAttrib
- ursina.vec2.Vec2
- ursina.vec3.Vec3
- ursina.vec4.Vec4
- ursina.texture.Texture
- ursina.collider.Collider
- ursina.collider.BoxCollider
- ursina.collider.SphereCollider
- ursina.collider.MeshCollider
- ursina.collider.CapsuleCollider
- ursina.mesh.Mesh
- ursina.sequence.Sequence
- ursina.sequence.Func
- ursina.sequence.Wait
- ursina.ursinamath.lerp
- ursina.curve
- ursina.mesh_importer.load_model
- ursina.texture_importer.load_texture
- ursina.string_utilities.camel_to_snake
- ursina.string_utilities.print_warning
- ursina.ursinamath.Bounds
- ursina.ursinastuff.invoke
- ursina.ursinastuff.PostInitCaller
- ursina.color
- ursina.color.Color
- ursina.scene.instance
- ursina.scripts.property_generator.generate_properties_for_class
"""

import ursina
import builtins
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
from ursina.mesh import Mesh
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
from ursina.ursinastuff import invoke, PostInitCaller

from ursina import color
from ursina.color import Color
try:
    from ursina.scene import instance as scene
except:
    pass

_Ursina_instance = None
_warn_if_ursina_not_instantiated = True # gets set to True after Ursina.__init__() to ensure the correct order.

from ursina.scripts.property_generator import generate_properties_for_class
@generate_properties_for_class()
class Entity(NodePath, metaclass=PostInitCaller):
    """
    Base class for all objects in the Ursina engine.

    Attributes:
        rotation_directions (tuple): The rotation directions for the entity.
        default_shader: The default shader for the entity.
        default_values (dict): The default values for the entity's attributes.
    """
    rotation_directions = (-1,-1,1)
    default_shader = None
    default_values = {
        # 'parent':scene,
        'name':'entity', 'enabled':True, 'eternal':False, 'position':Vec3(0,0,0), 'rotation':Vec3(0,0,0), 'scale':Vec3(1,1,1), 'model':None, 'origin':Vec3(0,0,0),
        'shader':None, 'texture':None, 'texture_scale':Vec2(1,1), 'color':color.white, 'collider':None}

    def __init__(self, add_to_scene_entities=True, enabled=True, **kwargs):
        """
        Initialize the Entity.

        Args:
            add_to_scene_entities (bool, optional): Whether to add the entity to the scene entities. Defaults to True.
            enabled (bool, optional): Whether the entity is enabled. Defaults to True.
            **kwargs: Additional keyword arguments for setting attributes.
        """
        self._children = []
        super().__init__(self.__class__.__name__)

        self.name = camel_to_snake(self.__class__.__name__)
        self.ignore = False     # if True, will not try to run code.
        self.ignore_paused = False      # if True, will still run when application is paused. useful when making a pause menu for example.
        self.ignore_input = False

        self.parent = scene     # default parent is scene, which means it's in 3d space. to use UI space, set the parent to camera.ui instead.
        self.add_to_scene_entities = add_to_scene_entities # set to False to be ignored by the engine, but still get rendered.
        if add_to_scene_entities:
            scene.entities.append(self)

        self._shader_inputs = {}
        self.setPythonTag('Entity', self)   # for the raycast to get the Entity and not just the NodePath
        self.scripts = []   # add with add_script(class_instance). will assign an 'entity' variable to the script.
        self.animations = []
        self.hovered = False    # will return True if mouse hovers entity.
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

        if 'shader' not in kwargs and Entity.default_shader:
            kwargs['shader'] = Entity.default_shader

        # make sure things get set in the correct order. both colliders and texture need the model to be set first.
        for key in ('model', 'origin', 'origin_x', 'origin_y', 'origin_z', 'collider', 'shader', 'texture', 'texture_scale', 'texture_offset'):
            if key in kwargs:
                setattr(self, key, kwargs[key])
                del kwargs[key]


        for key, value in kwargs.items():
            setattr(self, key, value)

        self.enabled = enabled

        # look for @every decorator and start a looping Sequence for decorated method
        from ursina.scripts.every_decorator import every, get_class_name
        for method in every.decorated_methods:
            if get_class_name(method._func) == self.types[0]:
                self.animations.append(Sequence(Func(method, self), Wait(method._every.interval), loop=True, started=True, entity=self))
                print('append to animations:', self)


    def __post_init__(self):
        """
        Post-initialization method called after the entity is created.
        """
        if self.enabled and hasattr(self, 'on_enable'):
            self.on_enable()

        elif not self.enabled and hasattr(self, 'on_disable'):
            self.on_disable()



    def _list_to_vec(self, value):
        """
        Convert a list to a Vec2 or Vec3.

        Args:
            value (list): The list to convert.

        Returns:
            Vec2 or Vec3: The converted vector.
        """
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
        """
        Enable the entity.
        """
        self.enabled = True

    def disable(self):
        """
        Disable the entity.
        """
        self.enabled = False


    def enabled_getter(self):
        """
        Get the enabled state of the entity.

        Returns:
            bool: True if the entity is enabled, False otherwise.
        """
        return getattr(self, '_enabled', True)

    def enabled_setter(self, value):
        """
        Set the enabled state of the entity.

        Args:
            value (bool): True to enable the entity, False to disable it.
        """
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



    def model_setter(self, value):
        """
        Set the model for the entity.

        Args:
            value: The model to set. Can be a NodePath, a string (model asset name), or None.
        """
        if value is None:
            if self.model:
                self.model.removeNode()
                # print('removed model')
            self._model = value
            return

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
        """
        Get the color of the entity.

        Returns:
            Vec4: The color of the entity.
        """
        return getattr(self, '_color', color.white)

    def color_setter(self, value):
        """
        Set the color of the entity.

        Args:
            value (str, Vec4, or tuple): The color to set.
        """
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
        """
        Get the eternal state of the entity.

        Returns:
            bool: True if the entity is eternal, False otherwise.
        """
        return getattr(self, '_eternal', False)

    def eternal_setter(self, value):
        """
        Set the eternal state of the entity.

        Args:
            value (bool): True to make the entity eternal, False to make it non-eternal.
        """
        self._eternal = value
        for c in self.children + self.loose_children:
            c.eternal = value


    def double_sided_setter(self, value):
        """
        Set the double-sided state of the entity.

        Args:
            value (bool): True to make the entity double-sided, False to make it single-sided.
        """
        self._double_sided = value
        self.setTwoSided(value)


    def render_queue_getter(self):
        """
        Get the render queue value of the entity.

        Returns:
            int: The render queue value.
        """
        return getattr(self, '_render_queue', 0)

    def render_queue_setter(self, value):
        """
        Set the render queue value of the entity.

        Args:
            value (int): The render queue value.
        """
        self._render_queue = value
        if self.model:
            self.model.setBin('fixed', value)


    def parent_setter(self, value):
        """
        Set the parent of the entity.

        Args:
            value: The parent entity.
        """
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
        """
        Get the loose parent of the entity.

        Returns:
            The loose parent entity.
        """
        return getattr(self, '_loose_parent', None)

    def loose_parent_setter(self, value):
        """
        Set the loose parent of the entity.

        Args:
            value: The loose parent entity.
        """
        if hasattr(self, '_loose_parent') and self._loose_parent and hasattr(self._loose_parent, '_loose_children') and self in self._loose_parent._loose_children:
            self._loose_parent._loose_children.remove(self)

        if not hasattr(value, '_loose_children'):
            value.loose_children = []
        value._loose_children.append(self)

        self._loose_parent = value


    def world_parent_getter(self):
        """
        Get the world parent of the entity.

        Returns:
            The world parent entity.
        """
        return getattr(self, '_parent', None)

    def world_parent_setter(self, value):
        """
        Set the world parent of the entity.

        Args:
            value: The world parent entity.
        """
        if hasattr(self, '_parent') and self._parent and hasattr(self._parent, '_children') and self in self._parent._children:
            self._parent._children.remove(self)

        if hasattr(value, '_children') and self not in value._children:
            value._children.append(self)

        self.wrtReparentTo(value)
        self.enabled = self._enabled   # parenting will undo the .stash() done when setting .enabled to False, so reapply it here
        self._parent = value


    @property
    def types(self):
        """
        Get all class names including those this inherits from.

        Returns:
            list: A list of class names.
        """
        from inspect import getmro
        return [c.__name__ for c in getmro(self.__class__)]


    def visible_getter(self):
        """
        Get the visibility of the entity.

        Returns:
            bool: True if the entity is visible, False otherwise.
        """
        return getattr(self, '_visible', True)

    def visible_setter(self, value):
        """
        Set the visibility of the entity.

        Args:
            value (bool): True to make the entity visible, False to hide it.
        """
        self._visible = value
        if value:
            self.show()
        else:
            self.hide()

    def visible_self_getter(self):
        """
        Get the visibility of the entity itself, without affecting children.

        Returns:
            bool: True if the entity itself is visible, False otherwise.
        """
        return getattr(self, '_visible_self', True)

    def visible_self_setter(self, value):
        """
        Set the visibility of the entity itself, without affecting children.

        Args:
            value (bool): True to make the entity itself visible, False to hide it.
        """
        self._visible_self = value
        if not self.model:
            return
        if value:
            self.model.show()
        else:
            self.model.hide()


    def collider_getter(self):
        """
        Get the collider of the entity.

        Returns:
            Collider: The collider of the entity.
        """
        return getattr(self, '_collider', None)

    def collider_setter(self, value):
        """
        Set the collider for the entity.

        Args:
            value: The collider to set. Can be a Collider instance, a string (collider type), or None.
        """
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
        """
        Get the collision state of the entity.

        Returns:
            bool: True if the entity has collision enabled, False otherwise.
        """
        return getattr(self, '_collision', False)

    def collision_setter(self, value):
        """
        Set the collision state of the entity.

        Args:
            value (bool): True to enable collision, False to disable it.
        """
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
        """
        Get the on_click callback function.

        Returns:
            function: The on_click callback function.
        """
        return getattr(self, '_on_click', None)

    def on_click_setter(self, value):
        """
        Set the on_click callback function.

        Args:
            value (function): The on_click callback function.
        """
        if not callable(value):
            raise TypeError(f'on_click must be a callabe, not {type(value)}')
        self._on_click = value


    def origin_getter(self):
        """
        Get the origin of the entity.

        Returns:
            Vec3: The origin of the entity.
        """
        return getattr(self, '_origin', Vec3.zero)

    def origin_setter(self, value):
        """
        Set the origin of the entity.

        Args:
            value (Vec2, Vec3, or list): The origin to set.
        """
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.origin_z)

        self._origin = value

        if self.model:
            self.model.setPos(-value[0], -value[1], -value[2])


    def origin_x_getter(self):
        """
        Get the x-coordinate of the origin.

        Returns:
            float: The x-coordinate of the origin.
        """
        return self.origin[0]
    def origin_x_setter(self, value):
        """
        Set the x-coordinate of the origin.

        Args:
            value (float): The x-coordinate of the origin.
        """
        self.origin = Vec3(value, self.origin_y, self.origin_z)

    def origin_y_getter(self):
        """
        Get the y-coordinate of the origin.

        Returns:
            float: The y-coordinate of the origin.
        """
        return self.origin[1]
    def origin_y_setter(self, value):
        """
        Set the y-coordinate of the origin.

        Args:
            value (float): The y-coordinate of the origin.
        """
        self.origin = Vec3(self.origin_x, value, self.origin_z)

    def origin_z_getter(self):
        """
        Get the z-coordinate of the origin.

        Returns:
            float: The z-coordinate of the origin.
        """
        return self.origin[2]
    def origin_z_setter(self, value):
        """
        Set the z-coordinate of the origin.

        Args:
            value (float): The z-coordinate of the origin.
        """
        self.origin = Vec3(self.origin_x, self.origin_y, value)

    def world_position_getter(self):
        """
        Get the world position of the entity.

        Returns:
            Vec3: The world position of the entity.
        """
        return Vec3(self.get_position(scene))

    def world_position_setter(self, value):
        """
        Set the world position of the entity.

        Args:
            value (Vec2, Vec3, or list): The world position to set.
        """
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.z)

        self.setPos(scene, Vec3(value[0], value[1], value[2]))

    def world_x_getter(self):
        """
        Get the x-coordinate of the world position.

        Returns:
            float: The x-coordinate of the world position.
        """
        return self.getX(scene)
    def world_y_getter(self):
        """
        Get the y-coordinate of the world position.

        Returns:
            float: The y-coordinate of the world position.
        """
        return self.getY(scene)
    def world_z_getter(self):
        """
        Get the z-coordinate of the world position.

        Returns:
            float: The z-coordinate of the world position.
        """
        return self.getZ(scene)

    def world_x_setter(self, value):
        """
        Set the x-coordinate of the world position.

        Args:
            value (float): The x-coordinate of the world position.
        """
        self.setX(scene, value)
    def world_y_setter(self, value):
        """
        Set the y-coordinate of the world position.

        Args:
            value (float): The y-coordinate of the world position.
        """
        self.setY(scene, value)
    def world_z_setter(self, value):
        """
        Set the z-coordinate of the world position.

        Args:
            value (float): The z-coordinate of the world position.
        """
        self.setZ(scene, value)

    def position_getter(self):
        """
        Get the position of the entity.

        Returns:
            Vec3: The position of the entity.
        """
        return Vec3(*self.getPos())

    def position_setter(self, value):
        """
        Set the position of the entity.

        Args:
            value (Vec2, Vec3, or list): The position to set.
        """
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.z)

        self.setPos(value[0], value[1], value[2])

    def x_getter(self):
        """
        Get the x-coordinate of the position.

        Returns:
            float: The x-coordinate of the position.
        """
        return self.getX()
    def x_setter(self, value):
        """
        Set the x-coordinate of the position.

        Args:
            value (float): The x-coordinate of the position.
        """
        self.setX(value)

    def y_getter(self):
        """
        Get the y-coordinate of the position.

        Returns:
            float: The y-coordinate of the position.
        """
        return self.getY()
    def y_setter(self, value):
        """
        Set the y-coordinate of the position.

        Args:
            value (float): The y-coordinate of the position.
        """
        self.setY(value)

    def z_getter(self):
        """
        Get the z-coordinate of the position.

        Returns:
            float: The z-coordinate of the position.
        """
        return self.getZ()
    def z_setter(self, value):
        """
        Set the z-coordinate of the position.

        Args:
            value (float): The z-coordinate of the position.
        """
        self.setZ(value)

    @property
    def X(self):
        """
        Get the x-coordinate of the position as an integer.

        Returns:
            int: The x-coordinate of the position as an integer.
        """
        return int(self.x)
    @property
    def Y(self):
        """
        Get the y-coordinate of the position as an integer.

        Returns:
            int: The y-coordinate of the position as an integer.
        """
        return int(self.y)
    @property
    def Z(self):
        """
        Get the z-coordinate of the position as an integer.

        Returns:
            int: The z-coordinate of the position as an integer.
        """
        return int(self.z)

    def world_rotation_getter(self):
        """
        Get the world rotation of the entity.

        Returns:
            Vec3: The world rotation of the entity.
        """
        rotation = self.getHpr(scene)
        return Vec3(rotation[1], rotation[0], rotation[2]) * Entity.rotation_directions

    def world_rotation_setter(self, value):
        """
        Set the world rotation of the entity.

        Args:
            value (Vec2, Vec3, or list): The world rotation to set.
        """
        self.setHpr(scene, Vec3(value[1], value[0], value[2]) * Entity.rotation_directions)

    def world_rotation_x_getter(self):
        """
        Get the x-coordinate of the world rotation.

        Returns:
            float: The x-coordinate of the world rotation.
        """
        return self.world_rotation[0]

    def world_rotation_x_setter(self, value):
        """
        Set the x-coordinate of the world rotation.

        Args:
            value (float): The x-coordinate of the world rotation.
        """
        self.world_rotation = Vec3(value, self.world_rotation[1], self.world_rotation[2])

    def world_rotation_y_getter(self):
        """
        Get the y-coordinate of the world rotation.

        Returns:
            float: The y-coordinate of the world rotation.
        """
        return self.world_rotation[1]

    def world_rotation_y_setter(self, value):
        """
        Set the y-coordinate of the world rotation.

        Args:
            value (float): The y-coordinate of the world rotation.
        """
        self.world_rotation = Vec3(self.world_rotation[0], value, self.world_rotation[2])

    def world_rotation_z_getter(self):
        """
        Get the z-coordinate of the world rotation.

        Returns:
            float: The z-coordinate of the world rotation.
        """
        return self.world_rotation[2]

    def world_rotation_z_setter(self, value):
        """
        Set the z-coordinate of the world rotation.

        Args:
            value (float): The z-coordinate of the world rotation.
        """
        self.world_rotation = Vec3(self.world_rotation[0], self.world_rotation[1], value)

    def rotation_getter(self):
        """
        Get the rotation of the entity.

        Returns:
            Vec3: The rotation of the entity.
        """
        rotation = self.getHpr()
        return Vec3(rotation[1], rotation[0], rotation[2]) * Entity.rotation_directions

    def rotation_setter(self, value):
        """
        Set the rotation of the entity.

        Args:
            value (Vec2, Vec3, or list): The rotation to set.
        """
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.rotation_z)

        self.setHpr(Vec3(value[1], value[0], value[2]) * Entity.rotation_directions)

    def rotation_x_getter(self):
        """
        Get the x-coordinate of the rotation.

        Returns:
            float: The x-coordinate of the rotation.
        """
        return self.rotation.x
    def rotation_x_setter(self, value):
        """
        Set the x-coordinate of the rotation.

        Args:
            value (float): The x-coordinate of the rotation.
        """
        self.rotation = Vec3(value, self.rotation[1], self.rotation[2])

    def rotation_y_getter(self):
        """
        Get the y-coordinate of the rotation.

        Returns:
            float: The y-coordinate of the rotation.
        """
        return self.rotation.y
    def rotation_y_setter(self, value):
        """
        Set the y-coordinate of the rotation.

        Args:
            value (float): The y-coordinate of the rotation.
        """
        self.rotation = Vec3(self.rotation[0], value, self.rotation[2])

    def rotation_z_getter(self):
        """
        Get the z-coordinate of the rotation.

        Returns:
            float: The z-coordinate of the rotation.
        """
        return self.rotation.z
    def rotation_z_setter(self, value):
        """
        Set the z-coordinate of the rotation.

        Args:
            value (float): The z-coordinate of the rotation.
        """
        self.rotation = Vec3(self.rotation[0], self.rotation[1], value)

    def quaternion_getter(self):
        """
        Get the quaternion rotation of the entity.

        Returns:
            Quat: The quaternion rotation of the entity.
        """
        return self.get_quat()
    def quaternion_setter(self, value):
        """
        Set the quaternion rotation of the entity.

        Args:
            value (Quat): The quaternion rotation to set.
        """
        self.set_quat(value)

    def world_scale_getter(self):
        """
        Get the world scale of the entity.

        Returns:
            Vec3: The world scale of the entity.
        """
        return Vec3(*self.getScale(scene))
    def world_scale_setter(self, value):
        """
        Set the world scale of the entity.

        Args:
            value (Vec2, Vec3, or list): The world scale to set.
        """
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)

        if isinstance(value, Vec2):
            value = Vec3(*value, self.scale_z)

        value = Vec3(*[e if e!=0 else .001 for e in value])
        self.setScale(scene, value)

    def world_scale_x_getter(self):
        """
        Get the x-coordinate of the world scale.

        Returns:
            float: The x-coordinate of the world scale.
        """
        return self.getScale(scene)[0]
    def world_scale_x_setter(self, value):
        """
        Set the x-coordinate of the world scale.

        Args:
            value (float): The x-coordinate of the world scale.
        """
        value = value if value != 0 else .001 # prevent panda3d erroring when scale is 0
        self.setScale(scene, Vec3(value, self.world_scale_y, self.world_scale_z))

    def world_scale_y_getter(self):
        """
        Get the y-coordinate of the world scale.

        Returns:
            float: The y-coordinate of the world scale.
        """
        return self.getScale(scene)[1]
    def world_scale_y_setter(self, value):
        """
        Set the y-coordinate of the world scale.

        Args:
            value (float): The y-coordinate of the world scale.
        """
        value = value if value != 0 else .001  # prevent panda3d erroring when scale is 0
        self.setScale(scene, Vec3(self.world_scale_x, value, self.world_scale_z))

    def world_scale_z_getter(self):
        """
        Get the z-coordinate of the world scale.

        Returns:
            float: The z-coordinate of the world scale.
        """
        return self.getScale(scene)[2]
    def world_scale_z_setter(self, value):
        """
        Set the z-coordinate of the world scale.

        Args:
            value (float): The z-coordinate of the world scale.
        """
        value = value if value != 0 else .001  # prevent panda3d erroring when scale is 0
        self.setScale(scene, Vec3(self.world_scale_x, self.world_scale_y, value))

    def scale_getter(self):
        """
        Get the scale of the entity.

        Returns:
            Vec3: The scale of the entity.
        """
        scale = self.getScale()
        return Vec3(scale[0], scale[1], scale[2])

    def scale_setter(self, value):
        """
        Set the scale of the entity.

        Args:
            value (Vec2, Vec3, or list): The scale to set.
        """
        if not isinstance(value, (Vec2, Vec3)):
            value = self._list_to_vec(value)
        if isinstance(value, Vec2):
            value = Vec3(*value, self.scale_z)

        value = [e if e!=0 else .001 for e in value]
        self.setScale(value[0], value[1], value[2])

    def scale_x_getter(self):
        """
        Get the x-coordinate of the scale.

        Returns:
            float: The x-coordinate of the scale.
        """
        return self.scale[0]
    def scale_x_setter(self, value):

        """
        Set the x-coordinate of the scale.

        Args:
            value (float): The x-coordinate of the scale.
        """

        value = value if value != 0 else .001 # prevent panda3d erroring when scale is 0

        self.setScale(value, self.scale_y, self.scale_z)

    def scale_y_getter(self):
        """
        Get the y-coordinate of the scale.

        Returns:
            float: The y-coordinate of the scale.
        """
        return self.scale[1]
    def scale_y_setter(self, value):

        """
        Set the y-coordinate of the scale.

        Args:
            value (float): The y-coordinate of the scale.
        """
        value = value if value != 0 else .001 # prevent panda3d erroring when scale is 0
        self.setScale(self.scale_x, value, self.scale_z)

    def scale_z_getter(self):
        """
        Get the z-coordinate of the scale.

        Returns:
            float: The z-coordinate of the scale.
        """
        return self.scale[2]
    def scale_z_setter(self, value):
        """
        Set the z-coordinate of the scale.

        Args:
            value (float): The z-coordinate of the scale.
        """
        value = value if value != 0 else .001 # prevent panda3d erroring when scale is 0
        self.setScale(self.scale_x, self.scale_y, value)

    def transform_getter(self):
        """
        Get the transform of the entity (position, rotation, scale).

        Returns:
            tuple: The transform of the entity (position, rotation, scale).
        """
        return (self.position, self.rotation, self.scale)
    def transform_setter(self, value):
        """
        Set the transform of the entity (position, rotation, scale).

        Args:
            value (tuple): The transform to set (position, rotation, scale).
        """
        self.position, self.rotation, self.scale = value

    def world_transform_getter(self):
        """
        Get the world transform of the entity (world_position, world_rotation, world_scale).

        Returns:
            tuple: The world transform of the entity (world_position, world_rotation, world_scale).
        """
        return (self.world_position, self.world_rotation, self.world_scale)
    def world_transform_setter(self, value):
        """
        Set the world transform of the entity (world_position, world_rotation, world_scale).

        Args:
            value (tuple): The world transform to set (world_position, world_rotation, world_scale).
        """
        self.world_position, self.world_rotation, self.world_scale = value


    @property
    def forward(self):
        """
        Get the forward direction of the entity.

        Returns:
            Vec3: The forward direction of the entity.
        """
        return Vec3(*scene.getRelativeVector(self, (0, 0, 1)))
    @property
    def back(self):
        """
        Get the backward direction of the entity.

        Returns:
            Vec3: The backward direction of the entity.
        """
        return -self.forward
    @property
    def right(self):
        """
        Get the right direction of the entity.

        Returns:
            Vec3: The right direction of the entity.
        """
        return Vec3(*scene.getRelativeVector(self, (1, 0, 0)))
    @property
    def left(self):
        """
        Get the left direction of the entity.

        Returns:
            Vec3: The left direction of the entity.
        """
        return -self.right
    @property
    def up(self):
        """
        Get the upward direction of the entity.

        Returns:
            Vec3: The upward direction of the entity.
        """
        return Vec3(*scene.getRelativeVector(self, (0, 1, 0)))
    @property
    def down(self):
        """
        Get the downward direction of the entity.

        Returns:
            Vec3: The downward direction of the entity.
        """
        return -self.up

    @property
    def screen_position(self):
        """
        Get the screen position (UI space) from world space.

        Returns:
            Vec2: The screen position of the entity.
        """
        from ursina import camera
        world_pos = camera.getRelativePoint(self, Vec3.zero)
        projected_pos = camera.lens.getProjectionMat().xform(Vec4(*world_pos, 1))
        reciprocal_w = 1 / projected_pos[3] if projected_pos[3] > 0 else 1
        normalized_pos = projected_pos * reciprocal_w
        return Vec2(normalized_pos[0] * camera.aspect_ratio / 2, normalized_pos[1] / 2)


    def shader_setter(self, value):
        """
        Set the shader for the entity.

        Args:
            value: The shader to set. Can be a Panda3dShader, a string (shader name), or a Shader instance.
        """
        self._shader = value
        if not self.model:
            return

        if value is None:
            self.setShaderAuto()
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
        """
        Get the value of a shader input.

        Args:
            name (str): The name of the shader input.

        Returns:
            The value of the shader input.
        """
        return self._shader_inputs.get(name, None)

    def set_shader_input(self, name, value):
        """
        Set the value of a shader input.

        Args:
            name (str): The name of the shader input.
            value: The value to set.
        """
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
        """
        Get the shader inputs of the entity.

        Returns:
            dict: The shader inputs of the entity.
        """
        return self._shader_inputs

    def shader_input_setter(self, value):
        """
        Set the shader inputs of the entity.

        Args:
            value (dict): The shader inputs to set.
        """
        for key, value in value.items():
            self.set_shader_input(key, value)


    def material_setter(self, value):
        """
        Set the material for the entity.

        Args:
            value (dict): The material to set.
        """
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


    def texture_setter(self, value):
        """
        Set the texture for the entity.

        Args:
            value: The texture to set. Can be a string (texture name), a Texture instance, or None.
        """
        if value is None and self.texture:
            # print('remove texture')
            self._texture = None
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
        """
        Get the texture scale of the entity.

        Returns:
            Vec2: The texture scale of the entity.
        """
        if 'texture_scale' in self._shader_inputs:
            return self._shader_inputs['texture_scale']
        else:
            return Vec2(1,1)

    def texture_scale_setter(self, value):
        """
        Set the texture scale for the entity.

        Args:
            value (Vec2 or list): The texture scale to set.
        """
        value = Vec2(*value)
        if self.model and self.texture:
            self.model.setTexScale(TextureStage.getDefault(), value[0], value[1])
            self.set_shader_input('texture_scale', value)

    def texture_offset_getter(self):
        """
        Get the texture offset of the entity.

        Returns:
            Vec2: The texture offset of the entity.
        """
        return getattr(self, '_texture_offset', Vec2(0,0))

    def texture_offset_setter(self, value):
        """
        Set the texture offset for the entity.

        Args:
            value (Vec2 or list): The texture offset to set.
        """
        value = Vec2(*value)
        if self.model and self.texture:
            self.model.setTexOffset(TextureStage.getDefault(), value[0], value[1])
            self.texture = self.texture
            self.set_shader_input('texture_offset', value)
        self._texture_offset = value

    def tileset_size_getter(self):
        """
        Get the tileset size of the entity.

        Returns:
            Vec2: The tileset size of the entity.
        """
        return self._tileset_size
    def tileset_size_setter(self, value):
        """
        Set the tileset size for the entity.

        Args:
            value (Vec2 or list): The tileset size to set.
        """
        self._tileset_size = value
        self.texture_scale = Vec2(1/value[0], 1/value[1])

    def tile_coordinate_getter(self):
        """
        Get the tile coordinate of the entity.

        Returns:
            Vec2: The tile coordinate of the entity.
        """
        return self._tile_coordinate
    def tile_coordinate_setter(self, value):
        """
        Set the tile coordinate for the entity.

        Args:
            value (Vec2 or list): The tile coordinate to set.
        """
        self._tile_coordinate = value
        self.texture_offset = Vec2(value[0] / self.tileset_size[0], value[1] / self.tileset_size[1])


    def alpha_getter(self):
        """
        Get the alpha (transparency) value of the entity.

        Returns:
            float: The alpha value of the entity.
        """
        return self.color[3]

    def alpha_setter(self, value):
        """
        Set the alpha (transparency) value of the entity.

        Args:
            value (float): The alpha value to set.
        """
        if value > 1:
            value = value / 255
        self.color = color.hsv(self.color.h, self.color.s, self.color.v, value)


    def always_on_top_setter(self, value):
        """
        Set the always_on_top state of the entity.

        Args:
            value (bool): True to make the entity always on top, False to disable it.
        """
        self._always_on_top = value
        self.set_bin("fixed", 0)
        self.set_depth_write(not value)
        self.set_depth_test(not value)


    def unlit_setter(self, value):
        """
        Set the unlit state of the entity.

        Args:
            value (bool): True to make the entity unlit, False to disable it.
        """
        self._unlit = value
        self.setLightOff(value)
        if value:
            self.hide(0b0001)
        else:
            self.show(0b0001)


    def billboard_setter(self, value):
        """
        Set the billboard state of the entity.

        Args:
            value (bool): True to make the entity always face the camera, False to disable it.
        """
        self._billboard = value
        if value:
            self.setBillboardPointEye(value)


    def wireframe_setter(self, value):
        """
        Set the wireframe state of the entity.

        Args:
            value (bool): True to render the model as wireframe, False to disable it.
        """
        self._wireframe = value
        self.setRenderModeWireframe(value)


    def generate_sphere_map(self, size=512, name=f'sphere_map_{len(scene.entities)}'):
        """
        Generate a sphere map for the entity.

        Args:
            size (int, optional): The size of the sphere map. Defaults to 512.
            name (str, optional): The name of the sphere map. Defaults to 'sphere_map_{len(scene.entities)}'.
        """
        from ursina import camera
        _name = 'textures/' + name + '.jpg'
        org_pos = camera.position
        camera.position = self.position
        application.base.saveSphereMap(_name, size=size)
        camera.position = org_pos

        # print('saved sphere map:', name)
        self.model.setTexGen(TextureStage.getDefault(), TexGenAttrib.MEyeSphereMap)
        self.reflection_map = name


    def generate_cube_map(self, size=512, name=f'cube_map_{len(scene.entities)}'):
        """
        Generate a cube map for the entity.

        Args:
            size (int, optional): The size of the cube map. Defaults to 512.
            name (str, optional): The name of the cube map. Defaults to 'cube_map_{len(scene.entities)}'.
        """
        from ursina import camera
        _name = 'textures/' + name
        org_pos = camera.position
        camera.position = self.position
        application.base.saveCubeMap(_name+'.jpg', size=size)
        camera.position = org_pos

        # print('saved cube map:', name + '.jpg')
        self.model.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldCubeMap)
        self.reflection_map = _name + '#.jpg'
        self.model.setTexture(builtins.loader.loadCubeMap(_name + '#.jpg'), 1)


    @property
    def model_bounds(self):
        """
        Get the bounds of the model.

        Returns:
            Bounds: The bounds of the model.
        """
        if self.model:
            if not self.model.getTightBounds():
                return Bounds(start=self.world_position, end=self.world_position, center=Vec3.zero, size=Vec3.zero)

            start, end = self.model.getTightBounds()
            start = Vec3(start)
            end = Vec3(end)
            center = (start + end) / 2
            size = end - start
            return Bounds(start=start, end=end, center=center, size=size)

        return None


    @property
    def bounds(self):
        """
        Get the bounds of the entity.

        Returns:
            Bounds: The bounds of the entity.
        """
        _bounds = self.model_bounds
        if _bounds is None:
            return None
        return Bounds(start=_bounds.start*self.scale, end=_bounds.end*self.scale, center=_bounds.center, size=_bounds.size*self.scale)


    def get_position(self, relative_to=scene):
        """
        Get the position of the entity relative to another entity.

        Args:
            relative_to: The entity to get the position relative to. Defaults to scene.

        Returns:
            Vec3: The position of the entity relative to the specified entity.
        """
        return Vec3(*self.getPos(relative_to))


    def set_position(self, value, relative_to=scene):
        """
        Set the position of the entity relative to another entity.

        Args:
            value (Vec2, Vec3, or list): The position to set.
            relative_to: The entity to set the position relative to. Defaults to scene.
        """
        self.setPos(relative_to, Vec3(value[0], value[1], value[2]))


    def rotate(self, value, relative_to=None):
        """
        Rotate the entity around its local axis.

        Args:
            value (Vec2, Vec3, or list): The rotation value.
            relative_to: The entity to rotate relative to. Defaults to self.
        """
        if not relative_to:
            relative_to = self

        self.setHpr(relative_to, Vec3(value[1], value[0], value[2]) * Entity.rotation_directions)


    def add_script(self, class_instance):
        """
        Add a script to the entity.

        Args:
            class_instance: The script class instance to add.

        Returns:
            The added script class instance.
        """
        if isinstance(class_instance, object) and not isinstance(class_instance, str):
            class_instance.entity = self
            class_instance.enabled = True
            self.scripts.append(class_instance)
            if hasattr(class_instance, 'on_script_added') and callable(class_instance.on_script_added):
                class_instance.on_script_added()
            # print('added script:', camel_to_snake(name.__class__.__name__))
            return class_instance


    def combine(self, analyze=False, auto_destroy=True, ignore=[], ignore_disabled=True, include_normals=False):
        """
        Combine the entity with its children into a single model.

        Args:
            analyze (bool, optional): Whether to analyze the model. Defaults to False.
            auto_destroy (bool, optional): Whether to automatically destroy the children. Defaults to True.
            ignore (list, optional): List of entities to ignore. Defaults to [].
            ignore_disabled (bool, optional): Whether to ignore disabled entities. Defaults to True.
            include_normals (bool, optional): Whether to include normals. Defaults to False.

        Returns:
            The combined model.
        """
        from ursina.scripts.combine import combine

        self.model = combine(self, analyze, auto_destroy, ignore, ignore_disabled, include_normals)
        return self.model


    def flipped_faces_setter(self, value):
        """
        Set the flipped faces state of the entity.

        Args:
            value (bool): True to flip the faces, False to disable it.
        """
        self._flipped_faces = value
        if value:
            self.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullClockwise))
        else:
            self.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))


    def look_at(self, target, axis=Vec3.forward):
        """
        Make the entity look at a target.

        Args:
            target (Entity, Vec3, or list): The target to look at.
            axis (Vec3 or str, optional): The axis to align with the target. Defaults to Vec3.forward.
        """
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


    def look_in_direction(self, direction, forward_axis):
        """
        Make the entity look in a specific direction.

        Args:
            direction (Vec3 or list): The direction to look in.
            forward_axis (Vec3 or str): The forward axis to align with the direction.
        """
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
            rotation_axis = cross_product(current_forward, direction)
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
        """
        Make the entity look at a target in 2D space.

        Args:
            target (Entity, Vec3, or list): The target to look at.
            axis (str, optional): The axis to align with the target. Defaults to 'z'.
        """
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
        """
        Make the entity look at a target in the XY plane.

        Args:
            target (Entity, Vec3, or list): The target to look at.
        """
        self.look_at_2d(target)
    def look_at_xz(self, target):
        """
        Make the entity look at a target in the XZ plane.

        Args:
            target (Entity, Vec3, or list): The target to look at.
        """
        self.look_at_2d(target, 'y')


    def has_ancestor(self, possible_ancestor):
        """
        Check if the entity has a specific ancestor.

        Args:
            possible_ancestor (Entity): The possible ancestor entity.

        Returns:
            bool: True if the entity has the specified ancestor, False otherwise.
        """
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

    def get_descendants(self, include_disabled=True):
        """
        Recursively get all descendants (children, grandchildren, and so on) of the entity.

        Args:
            include_disabled (bool, optional): Whether to include disabled descendants. Defaults to True.

        Returns:
            list: A list of all descendants.
        """
        descendants = []
        for child in self.children:
            if not include_disabled and not child.enabled:
                continue  # Skip disabled children if include_disabled is False
            descendants.append(child)
            descendants.extend(child.get_descendants(include_disabled))  # Recursive call
        return descendants


    def has_disabled_ancestor(self):
        """
        Check if the entity has a disabled ancestor.

        Returns:
            bool: True if the entity has a disabled ancestor, False otherwise.
        """
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
        """
        Get the children of the entity.

        Returns:
            list: A list of children entities.
        """
        return [e for e in getattr(self, '_children', []) if e]     # make sure list doesn't contain destroyed entities

    def children_setter(self, value):
        """
        Set the children of the entity.

        Args:
            value (list): A list of children entities.
        """
        self._children = value

    def loose_children_getter(self):
        """
        Get the loose children of the entity.

        Returns:
            list: A list of loose children entities.
        """
        return getattr(self, '_loose_children', [])


    @property
    def attributes(self):
        """
        Get the attribute names of the entity.

        Returns:
            tuple: A tuple of attribute names.
        """
        return ('name', 'enabled', 'eternal', 'visible', 'parent',
            'origin', 'position', 'rotation', 'scale',
            'shader', 'model', 'color', 'texture', 'texture_scale', 'texture_offset',
            'render_queue', 'always_on_top', 'collider', 'collision', 'scripts')

    def __str__(self):
        """
        Get the string representation of the entity.

        Returns:
            str: The string representation of the entity.
        """
        try:
            return self.name
        except:
            return '*destroyed entity*'

    def get_changes(self, target_class=None):
        """
        Get the changes made to the entity's attributes.

        Args:
            target_class (class, optional): The target class to compare against. Defaults to the entity's class.

        Returns:
            dict: A dictionary of attribute changes.
        """
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
        """
        Get the string representation of the entity with attribute changes.

        Returns:
            str: The string representation of the entity with attribute changes.
        """
        changes = self.get_changes(self.__class__)
        return f'{self.__class__.__name__}(' +  ''.join(f'{key}={value}, ' for key, value in changes.items()) + ')'


    def __deepcopy__(self, memo):
        """
        Create a deep copy of the entity.

        Args:
            memo: The memo dictionary for deep copy.

        Returns:
            The deep copy of the entity.
        """
        return eval(repr(self))


#------------
# ANIMATIONS
#------------

    def _getattr(self, name):
        """
        Get the value of an attribute.

        Args:
            name (str): The name of the attribute.

        Returns:
            The value of the attribute.
        """
        return getattr(self, name)

    def _setattr(self, name, value):
        """
        Set the value of an attribute.

        Args:
            name (str): The name of the attribute.
            value: The value to set.
        """
        setattr(self, name, value)

    def animate(self, name, value, duration=.1, delay=0, curve=curve.in_expo, loop=False, resolution=None, interrupt='kill', time_step=None, unscaled=False, ignore_paused=None, auto_play=True, auto_destroy=True, getattr_function=None, setattr_function=None):
        """
        Animate an attribute of the entity.

        Args:
            name (str): The name of the attribute to animate.
            value: The target value of the attribute.
            duration (float, optional): The duration of the animation. Defaults to .1.
            delay (float, optional): The delay before starting the animation. Defaults to 0.
            curve (function, optional): The curve function for the animation. Defaults to curve.in_expo.
            loop (bool, optional): Whether to loop the animation. Defaults to False.
            resolution (int, optional): The resolution of the animation. Defaults to None.
            interrupt (str, optional): The interrupt behavior ('kill' or 'finish'). Defaults to 'kill'.
            time_step (float, optional): The time step for the animation. Defaults to None.
            unscaled (bool, optional): Whether to use unscaled time. Defaults to False.
            ignore_paused (bool, optional): Whether to ignore paused state. Defaults to None.
            auto_play (bool, optional): Whether to automatically play the animation. Defaults to True.
            auto_destroy (bool, optional): Whether to automatically destroy the animation. Defaults to True.
            getattr_function (function, optional): The function to get the attribute value. Defaults to None.
            setattr_function (function, optional): The function to set the attribute value. Defaults to None.

        Returns:
            Sequence: The animation sequence.
        """
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
            sequence.append(Func(setattr_function, name, lerp(getattr_function(name), value, t)), regenerate=False)

        sequence.generate()
        if auto_play:
            sequence.start()
        return sequence

    def animate_position(self, value, duration=.1, **kwargs):
        """
        Animate the position of the entity.

        Args:
            value (Vec2, Vec3, or list): The target position.
            duration (float, optional): The duration of the animation. Defaults to .1.
            **kwargs: Additional keyword arguments for the animation.

        Returns:
            tuple: The animation sequences for x, y, and z coordinates.
        """
        x = self.animate('x', value[0], duration,  **kwargs)
        y = self.animate('y', value[1], duration,  **kwargs)
        z = None
        if len(value) > 2:
            z = self.animate('z', value[2], duration, **kwargs)
        return x, y, z

    def animate_rotation(self, value, duration=.1,  **kwargs):
        """
        Animate the rotation of the entity.

        Args:
            value (Vec2, Vec3, or list): The target rotation.
            duration (float, optional): The duration of the animation. Defaults to .1.
            **kwargs: Additional keyword arguments for the animation.

        Returns:
            tuple: The animation sequences for x, y, and z coordinates.
        """
        x = self.animate('rotation_x', value[0], duration,  **kwargs)
        y = self.animate('rotation_y', value[1], duration,  **kwargs)
        z = self.animate('rotation_z', value[2], duration,  **kwargs)
        return x, y, z

    def animate_scale(self, value, duration=.1, **kwargs):
        """
        Animate the scale of the entity.

        Args:
            value (Vec2, Vec3, or list): The target scale.
            duration (float, optional): The duration of the animation. Defaults to .1.
            **kwargs: Additional keyword arguments for the animation.

        Returns:
            Sequence: The animation sequence.
        """
        if isinstance(value, (int, float, complex)):
            value = Vec3(value, value, value)
        elif isinstance(value, tuple) and len(value) == 2:
            value = Vec3(*value, self.z)

        return self.animate('scale', value, duration=duration, **kwargs)


    def animate_shader_input(self, name, value, **kwargs):
        """
        Animate a shader input of the entity.

        Args:
            name (str): The name of the shader input.
            value: The target value of the shader input.
            **kwargs: Additional keyword arguments for the animation.

        Returns:
            Sequence: The animation sequence.
        """
        # instead of setting entity variables, set shader input
        return self.animate(name, value, getattr_function=self.get_shader_input, setattr_function=self.set_shader_input, **kwargs)


    # generate animation functions
    for e in ('x', 'y', 'z', 'rotation_x', 'rotation_y', 'rotation_z', 'scale_x', 'scale_y', 'scale_z'):
        exec(dedent(f'''
            def animate_{e}(self, value, duration=.1, delay=0, unscaled=False, **kwargs):
                return self.animate('{e}', value, duration=duration, delay=delay, unscaled=unscaled, **kwargs)
        '''))


    def shake(self, duration=.2, magnitude=1, speed=.05, direction=(1,1), delay=0, attr_name='position', interrupt='finish', unscaled=False, ignore_paused=True):
        """
        Shake the entity.

        Args:
            duration (float, optional): The duration of the shake. Defaults to .2.
            magnitude (float, optional): The magnitude of the shake. Defaults to 1.
            speed (float, optional): The speed of the shake. Defaults to .05.
            direction (tuple, optional): The direction of the shake. Defaults to (1,1).
            delay (float, optional): The delay before starting the shake. Defaults to 0.
            attr_name (str, optional): The attribute to shake. Defaults to 'position'.
            interrupt (str, optional): The interrupt behavior ('kill' or 'finish'). Defaults to 'finish'.
            unscaled (bool, optional): Whether to use unscaled time. Defaults to False.
            ignore_paused (bool, optional): Whether to ignore paused state. Defaults to True.

        Returns:
            Sequence: The shake sequence.
        """
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
        """
        Animate the color of the entity.

        Args:
            value (Color): The target color.
            duration (float, optional): The duration of the animation. Defaults to .1.
            interrupt (str, optional): The interrupt behavior ('kill' or 'finish'). Defaults to 'finish'.
            unscaled (bool, optional): Whether to use unscaled time. Defaults to False.
            **kwargs: Additional keyword arguments for the animation.

        Returns:
            Sequence: The animation sequence.
        """
        return self.animate('color', value, duration, **kwargs)

    def fade_out(self, value=0, duration=.5, unscaled=False, **kwargs):
        """
        Fade out the entity.

        Args:
            value (float, optional): The target alpha value. Defaults to 0.
            duration (float, optional): The duration of the fade out. Defaults to .5.
            unscaled (bool, optional): Whether to use unscaled time. Defaults to False.
            **kwargs: Additional keyword arguments for the animation.

        Returns:
            Sequence: The fade out sequence.
        """
        return self.animate('color', Vec4(self.color[0], self.color[1], self.color[2], value), duration=duration, **kwargs)

    def fade_in(self, value=1, duration=.5, **kwargs):
        """
        Fade in the entity.

        Args:
            value (float, optional): The target alpha value. Defaults to 1.
            duration (float, optional): The duration of the fade in. Defaults to .5.
            **kwargs: Additional keyword arguments for the animation.

        Returns:
            Sequence: The fade in sequence.
        """
        return self.animate('color', Vec4(self.color[0], self.color[1], self.color[2], value), duration=duration, **kwargs)

    def blink(self, value=ursina.color.clear, duration=.1, delay=0, curve=curve.in_expo_boomerang, interrupt='finish', **kwargs):
        """
        Blink the entity.

        Args:
            value (Color, optional): The target color. Defaults to ursina.color.clear.
            duration (float, optional): The duration of the blink. Defaults to .1.
            delay (float, optional): The delay before starting the blink. Defaults to 0.
            curve (function, optional): The curve function for the blink. Defaults to curve.in_expo_boomerang.
            interrupt (str, optional): The interrupt behavior ('kill' or 'finish'). Defaults to 'finish'.
            **kwargs: Additional keyword arguments for the animation.

        Returns:
            Sequence: The blink sequence.
        """
        return self.animate_color(value, duration=duration, delay=delay, curve=curve, interrupt=interrupt, **kwargs)



    def intersects(self, traverse_target=scene, ignore:list=None, debug=False):
        """
        Check if the entity intersects with other entities.

        Args:
            traverse_target: The target to traverse for intersections. Defaults to scene.
            ignore (list, optional): List of entities to ignore. Defaults to None.
            debug (bool, optional): Whether to enable debug mode. Defaults to False.

        Returns:
            HitInfo: The hit information.
        """
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

    e = Entity(model='quad', color=color.orange, position=(0,0,1), scale=1.5, rotation=(0,0,45), texture='brick')

    '''example of inheriting Entity'''
    class Player(Entity):
        def __init__(self, **kwargs):
            """
            Initialize the Player entity.

            Args:
                **kwargs: Additional keyword arguments for setting attributes.
            """
            super().__init__()
            self.model='cube'
            self.color = color.red
            self.scale_y = 2

            for key, value in kwargs.items():
                setattr(self, key, value)

        # input and update functions gets automatically called by the engine
        def input(self, key):
            """
            Handle input events.

            Args:
                key (str): The input key.
            """
            if key == 'space':
                # self.color = self.color.inverse()
                self.animate_x(2, duration=1)

        def update(self):
            """
            Update the Player entity.
            """
            self.x += held_keys['d'] * time.dt * 10
            self.x -= held_keys['a'] * time.dt * 10

    player = Player(x=-1)


    # test
    e = Entity(model='cube', collider='box', texture='shore', texture_scale=Vec2(2), color=hsv(.3,1,.5))
    print(repr(e))
    # a = Entity()
    # b = Entity(parent=a)


    # e.animate_x(3, duration=2, delay=.5, loop=True)
    # e.animate_position(Vec3(1,1,1), duration=1, loop=True)
    # e.animate_rotation(Vec3(45,45,45))
    # e.animate_scale(2, duration=1, curve=curve.out_expo_boomerang, loop=True)
    # e.animate_color(color.green, loop=True)
    # e.shake()
    # e.fade_out(delay=.5)
    # e.fade_in(delay=2.5)
    # e.blink(color.red, duration=1, curve=curve.linear_boomerang, loop=True)

    app.run()
