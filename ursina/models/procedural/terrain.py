from ursina import *


def texture_to_height_values(heightmap, skip=1):
    from PIL import Image
    from numpy import asarray, flip, swapaxes

    heightmap = heightmap
    skip = skip    # should be power of two. only works with heightmap, not height_values.

    if not isinstance(heightmap, Texture):
        heightmap = load_texture(heightmap)
        if not heightmap:
            print('failed to load heightmap:', heightmap)
            return

    width, depth = heightmap.width//skip, heightmap.height//skip
    img = Image.open(heightmap.path).convert('L')
    if skip > 1:
        img = img.resize([width, depth], Image.ANTIALIAS)

    height_values = asarray(img)
    height_values = flip(height_values, axis=0)
    height_values = swapaxes(height_values, 0, 1)
    return height_values


class Terrain(Mesh):
    def __init__(self, heightmap='', height_values=None, skip=1, **kwargs):

        if heightmap:
            self.height_values = texture_to_height_values(heightmap, skip)

        elif height_values:
            self.height_values = height_values


        self.width = len(self.height_values)
        self.depth = len(self.height_values[0])
        self.aspect_ratio = self.width / self.depth
        super().__init__()
        self.generate()


    def generate(self):
        # copy this from Plane to avoid unnecessary init
        self.vertices = []
        self.triangles = []
        self.uvs = []
        self.normals = []

        _height_values = [[j/255 for j in i] for i in self.height_values]


        w, h = self.width, self.depth
        min_dim = min(w, h)

        centering_offset = Vec2(-.5, -.5)

        # create the plane
        i = 0
        for z in range(h):
            for x in range(w):

                self.vertices.append(Vec3(x/(w-0), _height_values[x][z], z/(h-0)) + Vec3(centering_offset.x, 0, centering_offset.y))
                self.uvs.append((x/w, z/h))

                if x > 0 and z > 0:
                    # self.triangles.append((i, i-1, i-w-1, i-w))
                    self.triangles.extend(((i-w-1, i-w, i), (i-w-1, i, i-1)))

                # normals
                if x > 0 and z > 0 and x < w-1 and z < h-1:
                    rl =  _height_values[x+1][z] - _height_values[x-1][z]
                    fb =  _height_values[x][z+1] - _height_values[x][z-1]
                    self.normals.append(Vec3(rl, 1, fb).normalized())
                else:
                    self.normals.append(Vec3(0,1,0))

                i += 1

        super().generate()



if __name__ == '__main__':
    app = Ursina()
    '''Terrain using an RGB texture as input'''
    terrain_from_heightmap_texture = Entity(model=Terrain('heightmap_1', skip=8), scale=(40,5,20), texture='heightmap_1')

    '''
    I'm just getting the height values from the previous terrain as an example, but you can provide your own.
    It should be a list of lists, where each value is between 0 and 255.
    '''
    hv = terrain_from_heightmap_texture.model.height_values.tolist()
    terrain_from_list = Entity(model=Terrain(height_values=hv), scale=(40,5,20), texture='heightmap_1', x=40)

    def input(key):
        if key == 'space':  # randomize the terrain
            terrain_from_list.model.height_values = [[random.uniform(0,255) for a in column] for column in terrain_from_list.model.height_values]
            terrain_from_list.model.generate()

    EditorCamera()
    Sky()

    player = Entity(model='sphere', color=color.azure, scale=.2, origin_y=-.5)
    hv = terrain_from_list.model.height_values

    def update():
        direction = Vec3(held_keys['d'] - held_keys['a'], 0, held_keys['w'] - held_keys['s']).normalized()
        player.position += direction * time.dt * 8
        player.y = terraincast(player.world_position, terrain_from_list, hv)





    app.run()
