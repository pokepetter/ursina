from ursina import *


app = Ursina(size=(1280, 720))


# player = Entity(model='cube', color=color.orange, scale_y=2)

hit_plane = Entity(model='plane', collider='box', scale=100, alpha=.2, visible=False)

# terrain = Entity(model=Terrain('desert_terrain_heightmap'), scale=128)

cursor = Entity(model='sphere', color=color.azure, scale=1)

# terrain = Mesh()

vertices, triangles = [], []
uvs = []
w, h = 16,16
# self.height_values = [[j/255 for j in i] for i in self.height_values]

centering_offset = Vec2(-.5, -.5)


min_dim = min(w, h)

# from ursina.shaders import lit_with_shadows_shader
terrain = Entity(model=Mesh(vertices=[], triangles=[], uvs=[], colors=[]), scale=(w,1,h), y=-.01, texture='grass', collider='box')
terrain.scale *= 5

# create the plane
i = 0
for z in range(h):
    for x in range(w):
        terrain.model.vertices.append(Vec3((x/min_dim)+(centering_offset.x), 0, (z/min_dim)+centering_offset.y))
        terrain.model.uvs.append((x/w, z/h))

        if x > 0 and z > 0:
            terrain.model.triangles.append((i, i-1, i-w-1, i-w-0))

        i += 1

# terrain.model.colors = [color.black for v in terrain.model.vertices]
terrain.model.generate()

terrain.model.height_values =[[0 for x in range(w)] for y in range(h)]
# from ursina.prefabs.first_person_controller import FirstPersonController

ec = EditorCamera(rotation_smoothing=0, enabled=1, rotation=(30,30,0))
# player = FirstPersonController()

# def generate_normals_for_heightmap

strength = 5
def update():
    if mouse.world_point:
        cursor.position = mouse.world_point

        if mouse.left:
            x = int(cursor.x/(terrain.scale_x/w) + w/2)
            z = int(cursor.z/(terrain.scale_z/h) + h/2)
            i = (z*(w)) + x

            heights = []
            for z_offset in range(-3, 3):
                for x_offset in range(-3, 3):
                    true_z, true_x = x+x_offset, z+z_offset
                    if true_x >= 0 and true_x+1 < w and true_z >= 0 and true_z+1 < h:
                        heights.append(terrain.model.height_values[true_x][true_z])
            average_height = sum(heights) / len(heights)
            # print('average:', average_height)
            for z_offset in range(-3, 3):
                for x_offset in range(-3, 3):
                    true_z, true_x = x+x_offset, z+z_offset
                    brush_falloff = 1 - (distance_2d((0,0), (x_offset,z_offset)) / 4)

                    if true_x >= 0 and true_x+1 < w and true_z >= 0 and true_z+1 < h:
                        if not held_keys['shift']:
                            if not held_keys['alt']:
                                terrain.model.height_values[true_z][true_x] += strength * brush_falloff * time.dt
                            else:
                                terrain.model.height_values[true_z][true_x] -= strength * brush_falloff * time.dt
                        else:   #smooth
                            terrain.model.height_values[true_z][true_x] = lerp(terrain.model.height_values[true_z][true_x], average_height, strength * brush_falloff * time.dt)

            terrain.model.vertices = []
            terrain.model.colors = []
            for z, column in enumerate(terrain.model.height_values):
                for x, row in enumerate(column):
                    terrain.model.vertices.append(Vec3(x/w, terrain.model.height_values[x][z], z/h) + Vec3(centering_offset.x, 0, centering_offset.y))
                    terrain.model.colors.append(hsv(0, 0, 1-(terrain.model.height_values[x][z]*1)))

            terrain.model.generate()

    pos = cursor.get_position(relative_to=terrain) + Vec3(.5,0,.5)
    if pos.x >= 0 and pos.x < 1 and pos.z >= 0 and pos.z < 1:
        pos *= Vec3(w,0,h)
        # print(int(pos.x), int(pos.z))
        cursor.y = terrain.model.height_values[int(pos.x)][int(pos.z)]
        x, _, z = pos
        # print(floor(x), floor(z))

        height_values = terrain.model.height_values
        point =     height_values[int(floor(x))][int(floor(z))]
        point_e =   height_values[int(min(w-1, ceil(x)))][int(floor(z))]
        point_n =   height_values[int(floor(x))][int(min(h-1, ceil(z)))]
        point_ne =  height_values[int(min(w-1, ceil(x)))][int(min(h-1, ceil(z)))]

        u0v0 = point * (ceil(x) - x) * (ceil(z) - z) # interpolated (x0, z0)
        u1v0 = point_e * (x - floor(x)) * (ceil(z) - z) # interpolated (x1, z0)
        u0v1 = point_n * (ceil(x) - x) * (z - floor(z)) # interpolated (x0, z1)
        u1v1 = point_ne * (x - floor(x)) * (z - floor(z)) # interpolated (x1, z1)

        _h = u0v0 + u1v0 + u0v1 + u1v1  #estimate
        cursor.y = _h * terrain.scale_y



def input(key):
    if key == 'tab':    # press tab to toggle edit/play mode
        ec.enabled = not ec.enabled
        player.enabled = not player.enabled

Sky()
# DirectionalLight().look_at(Vec3(-.5,-1,-1))
app.run()
