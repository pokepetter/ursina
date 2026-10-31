from ursina import *

from particle_effect import *

class ParticleEmitter( Entity ):
    def __init__( self, particle_class, **kwargs ):
        super().__init__(
            model = "quad",
            billboard = True,
            texture = "particle_emitter_2"
        )

        #Debug mode
        self.debug_mode = False

        #Random
        self.random_max = 5

        #Accessing the Particle Class
        self.particle_class = particle_class

        #Kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        #Debug Mode ?
        self.visible = self.debug_mode

    def update( self ):

        #Spawn particles
        if random.randint(0, self.random_max) == 0:
            new_particle = self.particle_class()
            new_particle.position = self.position
