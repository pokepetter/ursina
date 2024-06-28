from ursina import *
from ursina.prefabs.particle_manager import ParticleManager, Particle
import random


window.vsync = False
app = Ursina()


def generate_particle():
    return Particle(
        position=Vec3(
            random.random() * 5 - 2.5, random.random() * 0.5, random.random() * 5 - 2.5
        ),
        velocity=Vec3(
            random.random() * 3 - 1.5,
            random.random() * 3 + 2,
            random.random() * 3 - 1.5,
        ),
        lifetime=random.random() * 5 + 3,
        delay=random.random() * 4,
        init_scale=Vec2(random.random() * 0.5),
        end_scale=Vec2(random.random() * 0.2),
        init_color=Vec4(random.random(), random.random(), random.random(), 0) * 0.2
        + color.orange,
        end_color=Vec4(Vec3(random.random()), 1),
    )


def generate_particles(n):
    return [generate_particle() for _ in range(n)]


manager = ParticleManager(
    texture="radial_gradient",
    scale=1,
    particles=generate_particles(100_000),
    gravity=Vec3(0, 1, 0),
    position=Vec3(0, -3, 0),
    looping=True,
    culling=False,
)


def input(key):
    if key == "-":
        manager.simulation_speed -= 0.1
    if key == "+":
        manager.simulation_speed += 0.1


EditorCamera()

app.run()
