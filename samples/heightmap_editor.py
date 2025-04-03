from ursina import *


app = Ursina()


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
terrain = Entity(model=Mesh(vertices=[], triangles=[], uvs=[], colors=[]), scale=(w,1,h), y=-.01,
    # texture='grass',
collider='box')
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
gradient_colors = {
     '0'  : '#9d9867',
    '11'  : '#9b9563',
    '38'  : '#828131',
    '43'  : '#696327',
    '46'  : '#696327',
    '47'  : '#716d37',
    '49'  : '#6d6828',
    '51'  : '#675f26',
    '54'  : '#5d5b2a',
    '55'  : '#4c483e',
    '58'  : '#645c27',
    '60'  : '#433d2e',
    '62'  : '#5e5a3a',
    '66'  : '#4b473c',
    '73'  : '#3d3425',
    '78'  : '#3a3a39',
    '80'  : '#423d31',
    '82'  : '#2e2d29',
    '88'  : '#3d3c3a',
    '255'  : '#000000',
}
def make_gradient(index_color_dict):    # returns a list of 256 colors
    '''
    given a dict of positions and colors, interpolates the colors into a list of 256 colors
    example input: {'0':color.hex('#9d9867'), '38':color.hex('#828131'), '54':color.hex('#5d5b2a'), '255':color.hex('#000000')}
    '''
    gradient = [color.black for i in range(256)]

    gradient_color_keys = tuple(index_color_dict.keys())
    gradient_color_values = tuple(index_color_dict.values())

    for i in range(len(gradient_colors)):
        from_col = color.hex(gradient_color_values[i-1])
        to_col = color.hex(gradient_color_values[i])

        from_num = 0
        if i > 0:
            from_num = int(gradient_color_keys[i-1])
        to_num = int(gradient_color_keys[i])
        dist = to_num - from_num

        for j in range(dist):
            gradient[from_num+j] = lerp(from_col, to_col, j/dist)

    return gradient

gradient = make_gradient(gradient_colors)


strength = 5
def update():
    if mouse.world_point:
        cursor.position = mouse.world_point

        if mouse.left:
            x = int(cursor.x/(terrain.scale_x/w) + w/2)
            z = int(cursor.z/(terrain.scale_z/h) + h/2)

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
                    # terrain.model.colors.append(hsv(0, 0, 1-(terrain.model.height_values[x][z]*1)))
                    y = int(terrain.model.height_values[x][z]*16)
                    y = clamp(y, 0, 255)
                    terrain.model.colors.append(gradient[y])

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



# def input(key):
#     if key == 'tab':    # press tab to toggle edit/play mode
#         ec.enabled = not ec.enabled
#         player.enabled = not player.enabled

Sky()
# DirectionalLight().look_at(Vec3(-.5,-1,-1))
app.run()
