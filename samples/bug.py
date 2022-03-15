from ursina import *

app = Ursina()
window.color = color._32

pivot = Entity()
cubes = []
rings = []
random.seed(0)

sphere = Entity(model='sphere', color=color.black, scale=1)
n = 10

for z in range(5):
    ring = Entity(scale=z)
    rings.append(ring)
    for i in range(n):
        pivot.rotation_y = i * 360//n
        e = Entity(model='cube', texture='white_cube', parent=pivot, z=((z*z)+3)*.16, scale=.2*z)
        e.color = color.hsv(0,0,z/5) + (random.random()*.1)
        e.world_parent = ring

        cubes.append(e)

def update():
    for e in rings:
        rotation_speed = 5 - e.scale_x
        rotation_speed = math.pow(rotation_speed, 1.5)
        e.rotation_y += rotation_speed * time.dt * 10

    for e in cubes:
        rotation_speed = 5 - e.parent.scale_x
        rotation_speed = math.pow(rotation_speed, 1.5)
        e.rotation += Vec3(rotation_speed) * time.dt * 20

EditorCamera()
app.run()
