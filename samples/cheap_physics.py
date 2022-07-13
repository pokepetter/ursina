from ursina import *


app = Ursina(vsync=False, size=(1280,720))

physics_entities = []
walls = []


from ursina.shaders import lit_with_shadows_shader
Entity.default_shader = lit_with_shadows_shader
DirectionalLight().look_at(Vec3(1,-1,-1))

ground = Entity(model='plane', scale=32, texture='white_cube', texture_scale=Vec2(32), collider='box')

from ursina.prefabs.first_person_controller import FirstPersonController
player = FirstPersonController()

walls.append(ground)

def input(key):
    if key == 'left mouse down':
        e = Entity(model='cube', color=color.azure, velocity=Vec3(0), position=player.position+Vec3(0,1.5,0)+player.forward, collider='box')
        e.velocity = (camera.forward + Vec3(0,.5,0)) * 10
        physics_entities.append(e)

def update():
    for e in physics_entities:
        if e.intersects():
            e.velocity = lerp(e.velocity, Vec3(0), time.dt*10)
            continue

        e.velocity = lerp(e.velocity, Vec3(0), time.dt)
        e.velocity += Vec3(0,-1,0) * time.dt * 5
        e.position += (e.velocity + Vec3(0,-4,0)) * time.dt


Sky()
app.run()
