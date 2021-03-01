from ursina import *



class Terrain(Mesh):
    def __init__(self, heightmap, skip=1, **kwargs):
        from PIL import Image
        from numpy import asarray, flip, swapaxes

        self.heightmap = heightmap

        if not isinstance(heightmap, Texture):
            self.heightmap = load_texture(heightmap)
            if not self.heightmap:
                print('failed to load heightmap:', heightmap)
                return

        self.skip = skip    # should be power of two.
        self.width, self.depth = self.heightmap.width//skip, self.heightmap.height//skip
        self.aspect_ratio = self.width / self.depth

        img = Image.open(self.heightmap.path).convert('RGB')
        if self.skip > 1:
            img = img.resize([self.width, self.depth], Image.ANTIALIAS)

        self.height_values = asarray(img)
        self.height_values = flip(self.height_values, axis=0)
        self.height_values = swapaxes(self.height_values, 0, 1)

        # copy this from Plane to avoid unecessary init
        self.vertices, self.triangles = list(), list()
        self.uvs = list()
        self.normals = list()
        w, h = self.width, self.depth
        self.height_values = [[j[0]/255 for j in i] for i in self.height_values]


        centering_offset = Vec2(-.5, -.5)
        if self.aspect_ratio > 1: # offset should be different if the terrain is not 1:1
            centering_offset.x *= self.aspect_ratio
        else:
            centering_offset.y /= self.aspect_ratio

        min_dim = min(w, h)


        # create the plane
        i = 0
        for z in range(h+1):
            for x in range(w+1):

                y = self.height_values[x-(x==w)][z-(z==h)] # do -1 if the coordinate is not in range

                self.vertices.append(Vec3((x/min_dim)+(centering_offset.x), y, (z/min_dim)+centering_offset.y))
                self.uvs.append((x/w, z/h))

                if x > 0 and z > 0:
                    self.triangles.append((i, i-1, i-w-2, i-w-1))

                # normals
                if x > 0 and z > 0 and x < w-1 and z < h-1:
                    rl =  self.height_values[x+1][z] - self.height_values[x-1][z]
                    fb =  self.height_values[x][z+1] - self.height_values[x][z-1]
                    self.normals.append(Vec3(rl, 1, fb).normalized())
                else:
                    self.normals.append(Vec3(0,1,0))

                i += 1

        super().__init__(vertices=self.vertices, triangles=self.triangles, uvs=self.uvs, normals=self.normals, **kwargs)




if __name__ == '__main__':
    app = Ursina()
    e = Entity(model=Terrain('heightmap_1', skip=16), scale=(20,5,20), texture='heightmap_1')
    Entity(model='plane', scale=e.scale, color=color.red)
    EditorCamera()
    Sky()

    # test
    t = time.time()
    e.collider = 'mesh'
    print(time.time() - t)

    def input(key):
        if key == '-':
            e.scale *= .9


    # e.collider = 'mesh'
    # terrains = list()
    # for i in (1,2,4,8):
    #     e = Entity(model=Terrain('heightmap_1', skip=i), scale=(20,5,20))
    #     e.texture='heightmap_1'
    #     e.enabled = False
    #     terrains.append(e)
    #
    # EditorCamera()
    # # 20, 40, 80, 160
    # current_terrain = terrains[0]
    # current_terrain.enabled = True
    #
    # lod_level = 0
    # def set_lod_level(n):
    #     global lod_level, terrain
    #
    #     for e in terrains:
    #         e.enabled = False
    #     terrains[n].enabled = True
    #     current_terrain = terrains[n]
    #
    #     lod_level = n
    #
    # water = Entity(model='plane', collider='mesh', position=current_terrain.position, scale=current_terrain.scale)
    # cursor = Entity(model='sphere', color=color.red)
    #
    # def update():
    #     global lod_level
    #     dist = distance(camera.world_position, terrains[0].world_position)
    #     # print(dist, lod_level)
    #     if lod_level != 0 and dist < 20:
    #         set_lod_level(0)
    #     if lod_level != 1 and dist > 20 and dist < 40:
    #         set_lod_level(1)
    #     if lod_level != 2 and dist > 40 and dist < 80:
    #         set_lod_level(2)
    #     if lod_level != 3 and dist > 80 and dist < 160:
    #         set_lod_level(3)
    #
    #
    #     if water.hovered:
    #         cursor.position = mouse.world_point
    #         grid_x = mouse.point[0] + .5
    #         grid_z = mouse.point[2] + .5
    #         grid_x *= current_terrain.model.width
    #         grid_z *= current_terrain.model.depth
    #
    #         grid_x = int(grid_x)
    #         grid_z = int(grid_z)
    #
    #         if grid_x < 0 or grid_x > current_terrain.model.width or grid_z < 0 or grid_z > current_terrain.model.depth:
    #             return  # outside
    #
    #         cursor.y = current_terrain.model.height_values[grid_x][grid_z] * current_terrain.scale_y




    app.run()
