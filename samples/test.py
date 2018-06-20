from ursina import *

app = ursina()

# p = Entity()
# p.model = 'quad'
# p.texture = 'maysketch_04_16_sky_city'
for y in range(200):
    for x in range(14):
        q = Quad()
        q.x = x
        q.y = y

camera.z = -500

app.run()
