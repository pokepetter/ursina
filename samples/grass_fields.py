from ursina import *
from ursina.shaders import lit_with_shadows_shader
random.seed(0)

app = Ursina()

Entity(model='cube', y=150, color=color.red)

# Normally I'd load a heightmap texture, but for this example I'll include a heightmap texture in the script itself, as base64.
data = '''data:image/png;base64,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'''
heightmap = Texture(data)

terrain_model = Terrain(heightmap)
Entity.default_shader = lit_with_shadows_shader
# print(terrain_model.height_values.tolist())
terrain = Entity(model=terrain_model, texture='grass', texture_scale=(3,3), scale=128)
# Instead of using a texture on the terrain, map them to vertex colors.
# Later, we'll use these colors to tint the grass we place, so the grass match the ground.
for uv in terrain.model.uvs:
    x = uv[0] * terrain.texture_scale[0]
    y = uv[1] * terrain.texture_scale[1]
    x -= int(x)
    y -= int(y)
    x = int(x * terrain.texture.width)
    y = int(y * terrain.texture.height)
    terrain.model.colors.append(terrain.texture.get_pixel(x, y).tint(-.25))

terrain.model.generate()
terrain.texture = None

scene.fog_density = .003


# Use two quads crossing each other to create a grass model
quad_model = load_model('quad', use_deepcopy=True)
grass_models = [deepcopy(quad_model) for i in range(4)]
from ursina.ursinamath import rotate_around_point_2d
for i, mesh in enumerate(grass_models):
    p = Entity()
    Entity(parent=p, model='quad', rotation_y=i*(360/5), origin_y=-.5, scale=1.5)
    Entity(parent=p, model='quad', rotation_y=(i*(360/5))+90, origin_y=-.5, scale=1.5)
    p.combine()
    grass_models[i] = p.model

# Instead of generating blue noise from scratch, which could be slow, use a pre-generated looping pattern to get the same effect
blue_noise = Empty(
    width = 64,
    height = 64,
    pattern = [(40, 1), (47, 1), (22, 2), (8, 3), (16, 3), (58, 4), (29, 6), (51, 6), (38, 7), (45, 8), (15, 9), (4, 10), (23, 10), (34, 12), (9, 13), (53, 13), (60, 13), (42, 14), (19, 16), (3, 17), (31, 17), (51, 18), (12, 19), (24, 19), (38, 19), (45, 21), (61, 21), (6, 23), (16, 24), (29, 24), (55, 25), (36, 26), (21, 27), (49, 27), (42, 28), (61, 28), (4, 29), (12, 30), (33, 31), (25, 32), (52, 33), (2, 34), (45, 34), (59, 34), (38, 35), (11, 37), (28, 37), (19, 38), (4, 39), (34, 39), (48, 40), (54, 41), (61, 41), (22, 44), (29, 44), (8, 45), (37, 45), (42, 45), (14, 46), (1, 47), (51, 47), (58, 50), (25, 51), (32, 51), (46, 51), (5, 52), (19, 52), (12, 54), (38, 54), (54, 55), (28, 57), (62, 57), (6, 58), (41, 58), (48, 58), (20, 59), (13, 61), (56, 62)]
)

perlin_noise_pixels = load_texture('perlin_noise').pixels


density = .8
grass_parent = Entity(texture='grass_lump', double_sided=True, model='grass_combined')
grass_colors = list(set([colr.tint(.2) for colr in terrain.model.colors]))

def place_grass():
    for __X in range(-8,8,1):
        for __Z in range(-8,8,1):

            for pos in blue_noise.pattern:
                if random.random() < 1-density:
                    continue

                x = ((__X * blue_noise.width)  + pos[0]) * .125
                z = ((__Z * blue_noise.height) + pos[1]) * .125
                y, n = terraincast(Vec3(x,300,z), terrain, return_normals=True)
                if not y:
                    continue

                # if sample_bilinear(perlin_noise_pixels, x, y, clamp_if_outside=False) < .5:
                #     continue

                grass_parent.model.vertices.extend([(v*1)+Vec3(x,y,z) for v in random.choice(grass_models).vertices])

                random_color = random.choice(grass_colors)
                # random_color = color.white

                grass_parent.model.colors.extend([random_color, ] * len(grass_models[0].vertices))
                grass_parent.model.uvs.extend(grass_models[0].uvs)

    grass_parent.model.generate()
    # Since placing the grass can be slow, save the result to disk and load it instead of generating it again next time.
    grass_parent.model.save('grass_combined.bam')

if not grass_parent.model:
    grass_parent.model = Mesh()
    place_grass()


player = EditorCamera(model=Capsule(height=1.5), origin_y=-.75, color=color.orange)
camera.fov = 100
player_speed = 8
def update():
    player.position += player.forward * (held_keys['w'] - held_keys['s']) * time.dt * player_speed
    player.position += player.right * (held_keys['d'] - held_keys['a']) * time.dt * player_speed
    player.y = terraincast(player.world_position+Vec3(0,100,0), terrain)



def input(key):
    if key == 'space':
        grass_parent.model = Mesh()
        place_grass()

Sky()
DirectionalLight().look_at(Vec3(1,-1,1))
# window.size = Vec2(1920,1080)
# window.borderless = True
# window.editor_ui.enabled = False

app.run()
