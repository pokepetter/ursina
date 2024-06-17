from ursina import *

from particle_emitter import *
from particle_effect_pack import *

App = Ursina()

ParticleEmitter( ParticleEffectSmokeJet, position = (0, 0, 0), debug_mode = True)

ParticleEmitter( ParticleEffectStar, position = (3, 0, 0), debug_mode = True)

ParticleEmitter( ParticleEffectSpark, position = (6, 0, 0), debug_mode = True)

ParticleEmitter( ParticleEffectFire, position = (9, 0, 0), debug_mode = True)

Entity(model = "cube", texture = "white_cube")

EditorCamera()

App.run()
