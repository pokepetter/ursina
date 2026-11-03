from ursina import *
from ursina import curve
from particle_effect import *

class ParticleEffectSmokeJet( ParticleEffect ):
    def __init__( self ):
        super().__init__(
            texture = "smoke",
            velocity = Vec3(random.uniform(-0.5, 0.5), random.uniform(1, 3), random.uniform(-0.5, 0.5)),
            scale = Vec3(0, 0, 0),
            final_scale = Vec3(1, 1, 1) * random.uniform(1, 3),
            final_color = color.rgba(255, 255, 255, 0),
            life_time = random.uniform(1, 3)
        )

class ParticleEffectSmokeStatic( ParticleEffect ):
    def __init__( self ):
        super().__init__(
            texture = "smoke",
            velocity = Vec3(random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)),
            scale = Vec3(0, 0, 0),
            final_scale = Vec3(1, 1, 1) * random.uniform(1, 3),
            final_color = color.rgba(255, 255, 255, 0),
            life_time = random.uniform(1, 3)
        )

class ParticleEffectFire( ParticleEffect ):
    def __init__( self ):
        super().__init__(
            texture = f"default_textures/fire/fire_{random.randint(1, 3)}",
            velocity = Vec3(random.uniform(-0.5, 0.5), random.uniform(-0.1, 3), random.uniform(-0.5, 0.5)),
            scale = Vec3(0.8, 0.8, 0.8) * random.uniform(1, 3),
            final_scale = Vec3(0, 0, 0),
            final_color = color.rgba(255, 255, 255, 0),
            life_time = random.uniform(1, 3)
        )

class ParticleEffectStar( ParticleEffect ):
    def __init__( self ):
        super().__init__(
            texture = "star_2",
            velocity = Vec3(random.uniform(-3.5, 3.5), random.uniform(5, 10), random.uniform(-3.5, 3.5)),
            gravity = Vec3(0, -10, 0),
            scale = Vec3(1, 1, 1) * random.uniform(1, 3),
            final_scale = Vec3(0, 0, 0),
            final_color = color.rgba(0, 0, 0, 0),
            life_time = random.uniform(1, 3)
        )

class ParticleEffectSpark( ParticleEffect ):
    def __init__( self ):
        super().__init__(
            texture = "spark",
            velocity = Vec3(random.uniform(-3.5, 3.5), random.uniform(5, 10), random.uniform(-3.5, 3.5)),
            gravity = Vec3(0, -10, 0),
            scale = Vec3(0.3, 0.3, 0.3) * random.uniform(1, 3),
            final_scale = Vec3(0, 0, 0),
            final_color = color.rgba(255, 255, 255, 0),
            life_time = random.uniform(1, 3)
        )
