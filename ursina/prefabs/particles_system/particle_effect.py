from ursina import *
from ursina import curve

class ParticleEffect( Entity ):
    def __init__( self, **kwargs ):
        super().__init__()

        #Rendering
        self.model = "quad"
        self.texture = "star"
        self.billboard = True

        #Gravity and position
        self.gravity = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)

        #Coloring
        self.color = color.rgba(255, 255, 255, 255)
        self.final_color = color.rgba(255, 255, 255, 255)
        self.color_curve = curve.linear

        #Scaling
        self.scale = (1, 1, 1)
        self.final_scale = (0, 0, 0)
        self.scale_curve = curve.linear

        #Lifetime
        self.life_time = 1

        #Kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        #Animation
        self.animate_scale(self.final_scale, self.life_time, curve = self.scale_curve)
        self.animate_color(self.final_color, self.life_time, curve = self.color_curve)

        #Destroying
        destroy(self, self.life_time)

    def update( self ):
        #Updating physics
        self.position += self.velocity * time.dt
        self.velocity += self.gravity * time.dt
