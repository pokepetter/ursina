from ursina import *
from time import perf_counter
import pyperclip
import json
import re

app = Ursina()
application.hot_reloader.reset_camera_on_reload = False


e = Entity()

tileset_scene = load_blender_scene('tileset', reload=True)
# tiles.enabled = False
[setattr(e, 'texture', 'sang_2') for e in tileset_scene.children]
# tiles = {e.name : e.model for e in tiles.children}
tiles = tileset_scene.meshes


def rotate_point(point, deg):
    from math import pi, cos, sin

    angle_rad = -deg/180 * pi
    cos_angle = cos(angle_rad)
    sin_angle = sin(angle_rad)
    dx, y, dz = point

    return Vec3(dx*cos_angle - dz*sin_angle, y, dx*sin_angle + dz*cos_angle)


t = perf_counter()
# top = [Vec3(*v) for v in tiles['top'].vertices]

vertices = {}
shapes = ('fallback', 'top', 'wall', 'top_edge', 'top_inner_corner', 'top_corner', 'corner', 'inner_corner',
    'wall_to_floor', 'wall_to_floor_corner', 'wall_to_floor_inner_corner', 'wall_to_edge', 'wall_to_edge_flipped', 'wall_to_edge_back', 'wall_to_edge_back_flipped',
    'bottom', 'bottom_edge', 'bottom_corner', 'bottom_corner_flipped', 'wall_to_ceiling_corner')
for tile_name in shapes:

    vertices[f'{tile_name}'] = [Vec3(*v) for v in tiles[tile_name].vertices]

    for angle in range(90, 360, 90):
        vertices[f'{tile_name}_{angle}'] = [rotate_point(v, angle) for v in vertices[tile_name]]

vertices['fallback'] = [Vec3(*v)*1for v in tiles['fallback'].vertices]
print('----------', 'rotate meshes:', perf_counter() - t)

tilemap = load_texture('autoblock_test_level')
Entity(model='plane', texture=tilemap, scale=Vec3(tilemap.width, 1, tilemap.height), origin=(-.5,0,-.5), y=-.1)

voxels = [[[0 for z in range(tilemap.height)]for y in range(16)] for x in range(tilemap.width)]

for z in range(tilemap.height):
    for x in range(tilemap.width):
        pixel = tilemap.get_pixel(x, z)
        if pixel.v < .05:
            continue
        for y in range(int(pixel.v * 16)):
            voxels[x][y][z] = 1

point_renderer = Entity(model=Mesh(mode='point', thickness=.1), color=color.white)
# level = Entity(mo)
width = tilemap.width
height = 16
depth = tilemap.height

level = Entity(model=Mesh(),
    texture='sang_2'
    )

# from ursina.shaders import triplanar_shader
# level.shader = triplanar_shader
# level.set_shader_input('top_texture', level.texture)
import random
random.seed(0)
possible_colors = [color.white, color.red, color.green, color.blue].reverse()
top_variation_colors = []
for i, e in enumerate([color.white, color.white, hsv(180,.03,.99), hsv(210,.02,.99), hsv(240,.04,.99)]):
    top_variation_colors.extend((e, ) * (6-i))
# top_variation_colors = (color.white, color.white, color.white, color.white, color.red, color.red, color.red,  color.green, color.blue)
# (color.random_color().tint(.8),) * len(tiles['top'].colors)


c = Empty()

def add(type, pos, rotate=0, scale=Vec3(1,1,1), debug=False):
    rotate_str = ''
    if rotate:
        rotate_str = f'_{int(rotate)}'
    # print('add:', f'{type}{rotate_str}')
    level.model.vertices.extend((v*scale) + pos + Vec3(.5,0,.5) for v in vertices[f'{type}{rotate_str}'])
    level.model.uvs.extend(tiles[type].uvs)
    if not debug:
        level.model.colors.extend(tiles[type].colors)
    else:
        level.model.colors.extend([color.red for e in tiles[type].colors])

directions = (
    # Vec(0,-1,1), Vec(-1,-1,0), Vec(0,-1,0), Vec(1,-1,0), Vec(0,-1,-1),
    # Vec3(-1,0,1), Vec3(0,0,1), Vec3(1,0,1), Vec3(-1,0,0), Vec3(0,0,0), Vec3(1,0,0), Vec3(-1,0,-1), Vec3(0,0,-1), Vec3(1,0,-1),
    # Vec(0,1,1), Vec(-1,1,0), Vec(0,1,0), Vec(1,1,0), Vec(0,1,-1),

    [Vec3(0,1,0), Vec3(0,-1,0)],  # up, down
    [Vec3(0,0,1), Vec3(1,0,1), Vec3(1,0,0), Vec3(1,0,-1), Vec3(0,0,-1), Vec3(-1,0,-1), Vec3(-1,0,0), Vec3(-1,0,1)],       # n, ne, e, se, s, sw, w, nw (easier to rotate)
    [Vec3(0,1,1), Vec3(1,1,1), Vec3(1,1,0), Vec3(1,1,-1), Vec3(0,1,-1), Vec3(-1,1,-1), Vec3(-1,1,0), Vec3(-1,1,1)],
    [Vec3(0,-1,1), Vec3(1,-1,1), Vec3(1,-1,0), Vec3(1,-1,-1), Vec3(0,-1,-1), Vec3(-1,-1,-1), Vec3(-1,-1,0), Vec3(-1,-1,1)],
)
def generate_codes_for(code, value, unknown='?'):
    # '???' -> ['000', '001', '010', '011' '100', '101', '110', '111']
    number_of_possible_combinations = code.count(unknown)
    variable_indices = [i for i, e in enumerate(code) if e == unknown]

    codes_dict = {}
    for i in range(int(math.pow(2, number_of_possible_combinations))):  # get each possible binary number
        possible_combination = format(i, f'0{number_of_possible_combinations}b')
        code_variant = [char for char in code]

        for j, index in enumerate(variable_indices):
            code_variant[index] = possible_combination[j]

        codes_dict[''.join(code_variant)] = value
    return codes_dict


tile_mappings = {
    # '01_1111_11110000_????????': 'top',
    **generate_codes_for('01_11111111_????????_????????', 'top'),
    **generate_codes_for('11_111?0?11_111???11_111?????', 'wall'),
    **generate_codes_for('01_111?0?11_????????_????????', 'top_edge'),
    **generate_codes_for('01_1?000?11_????????_????????', 'top_corner'),
    **generate_codes_for('01_11101111_????????_????????', 'top_inner_corner'),
    **generate_codes_for('11_1?000?11_????????_????????', 'corner'),
    **generate_codes_for('11_11101111_111?1111_????????', 'inner_corner'),

    # **generate_codes_for('11_11111111_11100011_11111111', 'wall_to_floor'),
    **generate_codes_for('11_??111111_111?0?11_????????', 'wall_to_floor'),

    # **generate_codes_for('11_10111111_11101111_????????', 'wall_to_floor_corner'),
    **generate_codes_for('11_11111111_1?000?11_11111111', 'wall_to_floor_corner'),
    # **generate_codes_for('11_11111111_10000111_11111111', 'wall_to_floor_corner'),
    # **generate_codes_for('11_11111111_11000011_11111111', 'wall_to_floor_corner'),
    **generate_codes_for('11_1?111111_11101111_????????', 'wall_to_floor_inner_corner'),
    # **generate_codes_for('11_111???11_1?000?11_????????', 'wall_to_edge'),
    # **generate_codes_for('11_111?0?11_111?000_?????????', 'wall_to_edge_flipped'),
    # '111110011110000111': 'wall_to_edge',
    # '111111101111000011': 'wall_to_edge',
    # '111110011111000111': 'wall_to_edge',
    # '111111011111000011': 'wall_to_edge',
    # **generate_codes_for('11_11100011_1?000?11_????????', 'wall_to_edge'),
    # '11_11100111_10000111_11100111': 'wall_to_edge',
    # '11_11100011_11100001_11110011': 'wall_to_edge_flipped',


    # '111100111111100111': 'wall_to_edge_flipped',

    # '11111?0011111?000?': 'wall_to_edge_flipped',
    # '111110001111100000': 'wall_to_edge_flipped',
    # '111111001111100000': 'wall_to_edge_flipped',
    # '111111001111110000': 'wall_to_edge_flipped',
    # '111111011111100001': 'wall_to_edge_flipped',


    # **generate_codes_for('11_11101111_111?0?11_????????', 'wall_to_edge_back',),


    **generate_codes_for('11_11111011_111?0011_????????', 'wall_to_edge_back_flipped'),
    # '11_11111011_111?0011_11111?11': 'wall_to_edge_back_flipped',
    # '11_11111011_11100011_11111111': 'wall_to_edge_back_flipped',
    # '11_11111011_11110011_11111111': 'wall_to_edge_back_flipped',
    # '11_11111011_11110011_11111011': 'wall_to_edge_back_flipped',

    **generate_codes_for('11_111?0?11_1?000?11_????????', 'wall_to_edge'),
    # '11_111?0?11_1?000?11_????????': 'wall_to_edge',
    # '11_11100011_10000011_11100011': 'wall_to_edge',
    # '11_11100011_11000011_11100011': 'wall_to_edge',
    # '11_11100111_10000111_11100111': 'wall_to_edge',
    # '11_11100011_10000011_11111111': 'wall_to_edge',
    # '11_11100111_10000011_11111111': 'wall_to_edge',
    # '11_11100011_10000011_11100111': 'wall_to_edge',
    # '11_11100111_11000111_11100111': 'wall_to_edge',
    # '11_11100111_11000011_11111111': 'wall_to_edge',
    # '11_11110111_11000011_11111111': 'wall_to_edge',

    **generate_codes_for('11_111?0?11_111?000?_????????', 'wall_to_edge_flipped'),
    # '11_111?0?11_111?000?_????????'
    # '11_11100011_11100001_11110011': 'wall_to_edge_flipped',
    # '11_11100011_11100001_11100011': 'wall_to_edge_flipped',
    # '11_11100111_11100001_11111111': 'wall_to_edge_flipped',
    # '11_11100011_11100001_11111111': 'wall_to_edge_flipped',
    # '11_11100011_11100000_11100011': 'wall_to_edge_flipped',
    # '11_11110011_11110001_11110011': 'wall_to_edge_flipped',
    # '11_11110111_11100001_11111111': 'wall_to_edge_flipped',
    # '11_11100011_11100001_11101111': 'wall_to_edge_flipped',
    **generate_codes_for('11_11101111_11100?11_????????', 'wall_to_edge_back'),
    # '11_11101111_11100?11_????????': 'wall_to_edge_back',
    # '11_11101111_11100011_11111111': 'wall_to_edge_back',
    # '11_11101111_11100111_11111111': 'wall_to_edge_back',
    # '11_11101111_11100011_11101111': 'wall_to_edge_back',
    # '11_11101111_11100111_11101111': 'wall_to_edge_back',

    **generate_codes_for('10_111?0?11_111?0?11_????????', 'bottom_edge'),
    # '10_11100011_11100011_11100001': 'bottom_edge',
    # '10_11100011_11100011_11000000': 'bottom_edge',
    # '10_11100111_11100111_01000111': 'bottom_edge',
    # '10_11110011_11110011_11110001': 'bottom_edge',
    # '10_11100011_11100011_11000001': 'bottom_edge',
    # '10_11100111_11100111_11000111': 'bottom_edge',
    # '10_11110011_11100011_11000001': 'bottom_edge',
    # '10_11100111_11100111_11000111': 'bottom_edge',
    # '10_11100111_11100011_11000111': 'bottom_edge',
    # '10_11100011_11100011_11000111': 'bottom_edge',
    # '10_11110111_11110111_01110111': 'bottom_edge',
    # '10_11110111_11100111_01110111': 'bottom_edge',

    '10_11000011_11000011_11000000': 'bottom_corner',
    '10_11000011_11000011_11000001': 'bottom_corner',
    '10_10000011_10000011_10000011': 'bottom_corner',
    '10_11000011_10000011_11000011': 'bottom_corner',
    '10_10000011_10000011_10000001': 'bottom_corner',
    '10_11000011_11000011_11000011': 'bottom_corner',


    '10_11100001_11100001_11000001': 'bottom_corner_flipped',
    '10_11110001_11110001_11100001': 'bottom_corner_flipped',
    '10_11100001_11100001_11100000': 'bottom_corner_flipped',

    '11_11110011_11110011_11110000': 'wall_to_ceiling_corner',


    # '111111101111100011': 'wall_to_edge_back_flipped',
    # '111111101111110011': 'wall_to_edge_back_flipped',


    # **generate_codes_for('111110011111101111', 'wall'),
    # '11111000111101': 'wall',
    # '11111100111101': 'wall',
    # '11111001111101': 'wall',
    # '11111101111101': 'wall',

    # '01111000110000': 'top_edge',
    # '01111100110000': 'top_edge',
    # '01111001110000': 'top_edge',

    # '01100001110000': 'top_corner',
    # '01110000110000': 'top_corner',
    # '01110001110000': 'top_corner',
    # '01100000110000': 'top_corner',

    # '0111101111': 'top_inner_corner',

    # '111?000?11????': 'corner',
    # '1110000111': 'corner',
    # '1111000011': 'corner',
    # '1111000111': 'corner',

    # '111111111': 'top_inner_corner',
    # '1111101111': 'inner_corner',
    # **generate_codes_for('110011111111110111', 'wall_to_floor'),

    # **generate_codes_for('111011111111101111', 'wall_to_floor_corner'),
    # **generate_codes_for('11111111111?000?11', 'wall_to_corner'),
    # '111111111': 'wall_to_floor',
    # '111111111': 'wall_to_floor_corner',
    # '111111111111101111': 'wall_to_floor_inner_corner',
    # '111011111111101111': 'wall_to_floor_inner_corner',

    # '11111???111?000?11????????'
    # '111110011110000111': 'wall_to_edge',
    # '111111101111000011': 'wall_to_edge',
    # '111110011111000111': 'wall_to_edge',
    # '111111011111000011': 'wall_to_edge',
    # '111100111111100111': 'wall_to_edge_flipped',

    # '11111011111110001111111111

    # '111110001111100000': 'wall_to_edge_flipped',
    # '111111001111100000': 'wall_to_edge_flipped',
    # '111111001111110000': 'wall_to_edge_flipped',
    # '111111011111100001': 'wall_to_edge_flipped',


    # '111110111111100011': 'wall_to_edge_back',
    # '111110111111110011': 'wall_to_edge_back',
    # '111110111111100111': 'wall_to_edge_back',
    # '111111101111100011': 'wall_to_edge_back_flipped',
    # '111111101111110011': 'wall_to_edge_back_flipped',
    # '111111111': 'tri_corner_flipped',
}
# for key, value in tile_mappings.items():
#     print(key, value)

cubes = []
def voxels_to_autoblock():
    level.model.clear()
    [destroy(e) for e in cubes]

    w = len(voxels)
    h = len(voxels[0])
    d = len(voxels[0][0])
    # print(w,h,d)

    for z in range(d):
        for x in range(w):
            for y in range(h):
                if voxels[x][y][z] == 0:
                    continue
                pos = Vec3(x,y,z)

                code = get_code(x, y, z)
                print(code)

                if code == '11_11111111_11111111_11111111':
                    continue

                # if re.match('0111111111....', code):
                #     add('top', pos, 0)
                #     continue

                # print(code)

                found_shape = False
                for j in range(0, 4):
                    from collections import deque
                    up_down, middle, top, bottom = [deque(e) for e in code.split('_')]
                    for e in (middle, top, bottom):
                        e.rotate(-(j*2))
                    # middle = deque(code[2:10])
                    # middle.rotate(-(j*2))
                    # top_diagonals = deque(code[10:18])
                    # print(len(top_diagonals))
                    # top_diagonals.rotate(-(j*2))
                    # bottom_diagonals = deque(code[18:])
                    # bottom_diagonals.rotate(-(j*2))

                    rotated_code = f"{code[:2]}_{''.join(middle)}_{''.join(top)}_{''.join(bottom)}"
                    print('found:', rotated_code)

                    # for key, value in tile_mappings.items():
                    #     if re.match(key, rotated_code):
                    #         add(value, pos, j*90)
                    #         found_shape = True  # break outer
                    #         # print('found:', rotated_code, j)
                    #         break

                    if rotated_code in tile_mappings:
                        name = tile_mappings[rotated_code]
                        add(name, pos, j*90)
                        found_shape = True  # break outer
                        # print('found:', rotated_code, j)
                        break

                if found_shape:
                    continue

                add('fallback', pos, 0)
                # e = Entity(model='cube', collider='box', scale=.8, color=color.random_color(), position=pos, origin=Vec3(-.5,.0,-.5), on_click=Func(print_code, x, y, z))
                # cubes.append(e)

    level.model.generate()
    level.collider = 'mesh'
    point_renderer.model.generate()



def get_code(x, y, z):
    code = ''
    for i, section in enumerate(directions):
        for dir in section:
            try:
                code += str(voxels[int(x+dir.x)][int(y+dir.y)][int(z+dir.z)])
            except:
                code += '0'

        if i <= 2:
            code += '_'

    return code



from time import perf_counter
t = perf_counter()
voxels_to_autoblock()
print('-------------', perf_counter() - t)


from ursina.shaders import lit_with_shadows_shader

lit_with_shadows_shader.default_input['shadow_color'] = Vec4(0, .5, 1, .25)

level.shader = lit_with_shadows_shader

sun = DirectionalLight()
sun.look_at(Vec3(-.1,-.2,-.5))
Sky(color=color.dark_gray)

#
        # Entity(model='')
camera.fov = 100
EditorCamera(rotation=Vec3(34.0843, -22.7431, 0), position=Vec3(7.50639, 6.2855, 7.96499), rotation_smoothing=0, eternal=True)
cursor = Entity(model='wireframe_cube', origin=(-.5,0,-.5))

def input(key):
    global voxels
    global tile_mappings
    if mouse.hovered_entity == level and key == 'left mouse down':
        pos = Vec3(*[int(e) for e in mouse.world_point + Vec3(0,.5,0) - (mouse.world_normal*.5)])
        cursor.position = pos

    if mouse.hovered_entity and key == 'left mouse down' and (held_keys['alt'] or held_keys['control']):
        # print(mouse.world_point - (mouse.world_normal*.5))

        # if mouse.hovered_entity == level:
        #     if held_keys['alt']:
        #         pos = Vec3(*[int(e) for e in mouse.world_point+Vec3(0,.5,0)])
        #     else:
        if held_keys['control']:
            pos = [int(e)for e in mouse.world_point + (mouse.world_normal*1)]
        # elif mouse.hovered_entity in cubes:
        #     pos = mouse.hovered_entity.position + (mouse.world_normal*int(not held_keys['alt']))
        #     if mouse.normal.y == 1:
        #         pos.y += .5

        pos = [int(e) for e in pos]
        voxels[pos[0]][pos[1]][pos[2]] = int(not held_keys['alt'])
        voxels_to_autoblock()


    if held_keys['control'] and key == 's':
        with open('autoblock_3_level.json', 'w') as file:
            json.dump(voxels, file)
        with open('_tile_mappings_4.json', 'w') as file:
            # json.dump(tile_mappings, file, indent=2)
            for key, value in tile_mappings.items():
                file.write(f"{key}, {value[0]}, {value[1]}\n")


    if held_keys['control'] and key == 'l':
        load()


    if key in '1234567890rtyuiop' and mouse.hovered_entity == level:
        pos = cursor.position
        x,y,z = [int(e) for e in pos]
        code = get_code(x,y,z)
        print(code)
        pyperclip.copy(code)
        return

        # if key in '0123456789tyuio':
        #     i = '0123456789tyuio'.index(key)
        #     if not code in tile_mappings:
        #         tile_mappings[code] = (shapes[i], 0)
        #     else:
        #         tile_mappings[code] = (shapes[i], tile_mappings[code][1])
        #     voxels_to_autoblock()
        #
        # if key == 'r':
        #     angles = [0, 90, 180, 270]
        #     i = angles.index(tile_mappings[code][1]) + 1
        #     if i == 4:
        #         i = 0
        #     # print('--------', (tile_mappings[code][0], angles[i]))
        #     tile_mappings[code] = (tile_mappings[code][0], angles[i])
        #     voxels_to_autoblock()

def load():
    global voxels, tile_mappings
    with open('autoblock_3_level.json', 'r') as file:
        voxels = json.load(file)
    # with open('_tile_mappings_4.json', 'r') as file:
    #     tile_mappings = {}
    #     for l in file.readlines():
    #         code, model_name, rotation = l.split(', ')
    #         tile_mappings[code] = (model_name, int(rotation))
    voxels_to_autoblock()
load()

app.run()
