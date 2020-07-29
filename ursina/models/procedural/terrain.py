from ursina import *



class Terrain(Mesh):
    def __init__(self, heightmap, skip=1, **kwargs):
        from PIL import Image
        from numpy import asarray, flip


        self.heightmap = load_texture(heightmap)
        if not self.heightmap:
            print('failed to load heightmap:', heightmap)
            return

        self.skip = skip
        self.width, self.depth = self.heightmap.width//skip, self.heightmap.height//skip
        img = Image.open(self.heightmap.path)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img = img.transpose(Image.ROTATE_90)
        if self.skip > 1:
            img = img.resize([self.width, self.depth], Image.ANTIALIAS)
        self.height_values = asarray(img)
        self.height_values = flip(self.height_values, axis=0)

        # copy this from Plane to avoid unecessary init
        self.vertices, self.triangles = list(), list()
        self.uvs = list()
        self.normals = list()
        w, h = self.width, self.depth
        i = 0
        for z in range(h+1):
            for x in range(w+1):
                self.vertices.append(Vec3((x/w)-.5, 0, (z/h)-.5))
                self.uvs.append((x/w, z/h))
                if x > 0 and z > 0:
                    self.triangles.append((i, i-1, i-w-2, i-w-1))

                i += 1

        # super().__init__(subdivisions=(self.width, self.depth), **kwargs)

        i = 0
        t = time.time()
        self.height_values = [[j[0]/255 for j in i] for i in self.height_values]
        # return
        for z in range(self.depth+1):
            for x in range(self.width+1):

                if x < self.width and z < self.depth:
                    y = self.height_values[x][z]

                self.vertices[i] = Vec3(x/self.width -.5, y, z/self.depth -.5)

                if x > 0 and z > 0 and x < self.width-1 and z < self.width-1:
                    rl =  self.height_values[x+1][z] - self.height_values[x-1][z]
                    fb =  self.height_values[x][z+1] - self.height_values[x][z-1]
                    self.normals.append(Vec3(rl, 1, fb).normalized())
                else:
                    self.normals.append(Vec3(0,1,0))

                i += 1
                #
                # slope_limit = .1
                # if x > 0 and z > 0 and x < self.width-1 and z < self.depth-1:
                #     C = self.heightmap.get_pixel(x, z).r
                #     R = self.heightmap.get_pixel(x+1, z).r
                #     L = self.heightmap.get_pixel(x-1, z).r
                #     T = self.heightmap.get_pixel(x, z+1).r
                #     B = self.heightmap.get_pixel(x, z-1).r
                #     if abs(C-R) < slope_limit and abs(C-L) < slope_limit and abs(C-T) < slope_limit and abs(C-B) < slope_limit:
                #         self.colors.append(color.yellow)
                #     else:
                #         self.colors.append(color.dark_gray)
                # #     self.normals.append(Vec3(2*(R-L), -4, 2*(B-T)).normalized())
                # else:
                #     self.colors.append(color.dark_gray)

        super().__init__(vertices=self.vertices, triangles=self.triangles, uvs=self.uvs, normals=self.normals, **kwargs)




if __name__ == '__main__':
    app = Ursina()
    e = Entity(model=Terrain('heightmap_1', skip=2), scale=(20,5,20), texture='heightmap_1')
    EditorCamera()
    Sky()

    # test
    t = time.time()
    e.collider = 'mesh'
    print(time.time() - t)



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
