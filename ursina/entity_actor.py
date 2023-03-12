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
from direct.interval.ActorInterval import LerpAnimInterval

from panda3d.core import Shader as Panda3dShader
from ursina import shader
from ursina.shader import Shader
from ursina.ursinamath import Bounds

from ursina import color,Entity
from ursina.color import Color
try:
    from ursina.scene import instance as scene
except:
    pass


#Don't know what imports I do and don't need so im importing everything from entity.py

class AnimatedEntity(Entity, Actor):
    def __init__(self, model, animations=None, **kwargs):
        Actor.__init__(self, model, animations)
        self.entity = Entity(model=None, **kwargs)
        self.entity.model = self
        self.current_anim=None

    @property
    def model(self):
        return self.entity.model

    @model.setter
    def model(self, value):
        self.entity.model = value

    def LerpAnim(self,toanim,rate=1,part=None):
        current=self.get_current_anim()
        self.enableBlend()
        self.setPlayRate(rate,toanim,partName=part)
        if toanim==self.current_anim:
            pass     
        elif self.current_anim!=None:
            self.loop(toanim, partName=part)
            Interv=LerpAnimInterval(self, 0.25, self.current_anim, toanim, partName=part)
            Interv.start()
        elif self.current_anim==None:
            self.loop(toanim, partName=part)
            Interv=LerpAnimInterval(self, 0.25, current, toanim, partName=part)
            Interv.start()
            print(3)
        else: #This part doesnt work
            print(f"No animtion with name {toanim} found")
        self.current_anim=toanim

    

if __name__ == '__main__':
    from ursina import *
    app=Ursina()
    #Get your own model for it too work
    e1=AnimatedEntity(model='player.glb',color=color.red,scale=.05)
    e1.loop('idle')
    EditorCamera()
    def input(key):
        if key=='s':
            e1.color=color.white
            e1.LerpAnim('run')
        elif key=='w':
            e1.scale=1
            e1.LerpAnim('walk')
    app.run()