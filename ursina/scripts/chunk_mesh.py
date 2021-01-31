from ursina import *
from math import floor

app = Ursina()
t = time.time()

application.asset_folder = application.asset_folder.parent.parent
terrain = Entity(model=Terrain('grass_fields_heightmap', skip=8), texture='grass', texture_scale=(3,3), scale=256)


# grid = [[[None for z in range(8)] for y in range(1)] for x in range(8)] # make 2d array of entities
grid = [[None for z in range(8)] for x in range(8)] # make 2d array of entities

x_slices = 8
# y = 1
z_slices = 8

for z in range(z_slices):
    for x in range(x_slices):
        part = Entity(
            parent=terrain,
            x=(x/x_slices) - .5 + (1/x_slices/2),
            z=(z/z_slices) - .5 + (1/z_slices/2),
            color=color.random_color(),
            model=Mesh(),
            always_on_top=True
            )
        grid[x][z] = part

terrain.model.generated_vertices = [v+Vec3(.5,0.5) for v in terrain.model.generated_vertices]
for i in range(0, len(terrain.model.generated_vertices), 3):
    v = terrain.model.generated_vertices[i]
    x = floor(v.x * x_slices)
    z = floor(v.z * z_slices)
    x = min(x, x_slices-1)
    z = min(z, z_slices-1)

    offset = Vec3(- (x/x_slices) - (1/x_slices/2), -.5, -(z/z_slices) - (1/x_slices/2))
    grid[x][z].model.vertices.extend([
        terrain.model.generated_vertices[i]   + offset,
        terrain.model.generated_vertices[i+1] + offset,
        terrain.model.generated_vertices[i+2] + offset,
        ])


for z in range(z_slices):
    for x in range(x_slices):
        grid[x][z].model.generate()
        # Entity(parent=grid[x][z], model='cube', scale=.01, color=color.red, always_on_top=True)
        # grid[x][z].enabled = False

        grid[x][z].collider = 'mesh'
        # grid[x][z].model = None


from ursina.prefabs.first_person_controller import FirstPersonController
player = FirstPersonController(position=(0,200,0))
player.add_script(NoclipMode())
# player = EditorCamera(rotation_x=90, y=128)


def update():
    for part in terrain.children:
        part.enabled = distance_xz(part.world_position, player.world_position) < 256/8
        # print(distance_xz(part.world_position, camera.world_position), 256/4)






app.run()
