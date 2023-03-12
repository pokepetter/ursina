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
from ursina.collider import *
from direct.actor.Actor import Actor

from panda3d.core import Shader as Panda3dShader
from ursina import shader
from ursina.shader import Shader
from ursina.string_utilities import print_info, print_warning
from ursina.ursinamath import Bounds

from ursina import color,Entity
from ursina.color import Color
try:
    from ursina.scene import instance as scene
except:
    pass

class AnimatedEntity(Entity, Actor):
    def __init__(self, model, animations=None, **kwargs):
        Actor.__init__(self, model, animations)
        self.entity = Entity(model=None, **kwargs)
        self.entity.model = self

    @property
    def model(self):
        return self.entity.model

    @model.setter
    def model(self, value):
        self.entity.model = value
        

    def play_animation(self, anim_name):
        self.play(anim_name)
    def loop_animation(self, anim_name):
        self.loop(anim_name)

if __name__ == '__main__':
    from ursina import *
    app=Ursina()
    #Get your own model for it too work
    e1=AnimatedEntity(model='player.glb',color=color.red,scale=.01,x=-5)
    EditorCamera()
    def input(key):
        if key=='s':
            e1.loop_animation('walk')
    app.run()