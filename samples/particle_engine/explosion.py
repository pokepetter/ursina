"""
The explosion sprite sheet is from https://opengameart.org/content/arw-explosion.
Thanks to ColorOptimist for publishing the sprite sheet on opengameart.org
"""

from ursina import *
from ursina.prefabs.particle_manager import ParticleManager, Particle
import random


window.vsync = False
app = Ursina()


def generate_particle():
    return Particle(
        position=Vec3(
            random.random() *.2, random.random() * .2, random.random() * .2
        ),
        velocity=Vec3(
            random.random() - .5,
            random.random() - .5,
            random.random() - .5,
        )*5,
        lifetime=random.random() * .3 +.5,
        delay=random.random() * .05,
        init_scale=Vec3(random.random() * 0.1),
        end_scale=Vec3(random.random()*10),
        init_color=color.white,
        end_color=color.white,
    )


def generate_particles(n):
    return [generate_particle() for _ in range(n)]


manager = ParticleManager(
    scale=1,
    particles=generate_particles(100),
    gravity=Vec3(0, 1, 0),
    position=Vec3(0, 0, 0),
    model="quad",
    texture="explosion_sprite_sheet",
    frames=Vec2(8,1),
    frames_per_loop=8,
    billboard=True,
)


def input(key):
    if key == "space":
        manager.elapsed_time = 0
    if key == "-":
        manager.simulation_speed -= 0.1
    if key == "+":
        manager.simulation_speed += 0.1

window.color = color.black

EditorCamera()

app.run()

