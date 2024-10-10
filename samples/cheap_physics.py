from ursina import *
from ursina.shaders import lit_with_shadows_shader


app = Ursina(size=(1280,720))

physics_entities = []
class PhysicsEntity(Entity):
    def __init__(self, model='cube', collider='box', **kwargs):
        super().__init__(model=model, collider=collider, **kwargs)
        physics_entities.append(self)

    def update(self):
        if self.intersects():
            self.stop()
            return

        self.velocity = lerp(self.velocity, Vec3(0), time.dt)
        self.velocity += Vec3(0,-1,0) * time.dt * 5
        self.position += (self.velocity + Vec3(0,-4,0)) * time.dt

    def stop(self):
        self.velocity = Vec3(0,0,0)
        if self in physics_entities:
            physics_entities.remove(self)

    def on_destroy(self):
        self.stop()


    def throw(self, direction, force):
        pass


Entity.default_shader = lit_with_shadows_shader

ground = Entity(model='plane', scale=32, texture='white_cube', texture_scale=Vec2(32), collider='box', color=color.light_gray)
DirectionalLight().look_at(Vec3(1,-1,-1))

from ursina.prefabs.first_person_controller import FirstPersonController
player = FirstPersonController()
Sky()


def input(key):
    if key == 'left mouse down':
        e = PhysicsEntity(model='cube', color=color.azure, velocity=Vec3(0), position=player.position+Vec3(0,1.5,0)+player.forward, collider='sphere')
        e.velocity = (camera.forward + Vec3(0,.5,0)) * 10
        # physics_entities.append(e)


app.run()
