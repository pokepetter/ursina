from ursina import *


class Terrain(Plane):
    def __init__(self, heightmap, skip=1, store_height_values=False, **kwargs):
        self.heightmap = load_texture(heightmap)
        if not self.heightmap:
            print('failed to load heightmap:', heightmap)
            return

        self.skip = skip
        self.width, self.depth = self.heightmap.width//skip, self.heightmap.height//skip
        if self.skip > 1:
            from PIL import Image
            img = Image.open(self.heightmap.path)
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            img = img.resize([self.width, self.depth], Image.ANTIALIAS)
            self.heightmap = Texture(img)

        if store_height_values:
            self.height_values = [[0 for z in range(self.depth)] for x in range(self.width)]

        super().__init__(subdivisions=(self.width, self.depth), **kwargs)

        i = 0
        for z in range(self.depth+1):
            for x in range(self.width+1):

                if x < self.width and z < self.depth:
                    y = self.heightmap.get_pixel(x, z).r
                    if store_height_values:
                        self.height_values[x][z] = y

                self.vertices[i] = Vec3(x/self.width -.5, y, z/self.depth -.5)
                i += 1

        self.generate()




if __name__ == '__main__':
    app = Ursina()

    terrains = list()
    for i in (1,2,4,8):
        e = Entity(model=Terrain('heightmap_1', skip=i, store_height_values=True), scale=(20,5,20))
        e.texture='heightmap_1'
        e.enabled = False
        terrains.append(e)

    EditorCamera()
    # 20, 40, 80, 160
    current_terrain = terrains[0]
    current_terrain.enabled = True

    lod_level = 0
    def set_lod_level(n):
        global lod_level, terrain

        for e in terrains:
            e.enabled = False
        terrains[n].enabled = True
        current_terrain = terrains[n]

        lod_level = n

    water = Entity(model='plane', collider='mesh', position=current_terrain.position, scale=current_terrain.scale)
    cursor = Entity(model='sphere', color=color.red)

    def update():
        global lod_level
        dist = distance(camera.world_position, terrains[0].world_position)
        # print(dist, lod_level)
        if lod_level != 0 and dist < 20:
            set_lod_level(0)
        if lod_level != 1 and dist > 20 and dist < 40:
            set_lod_level(1)
        if lod_level != 2 and dist > 40 and dist < 80:
            set_lod_level(2)
        if lod_level != 3 and dist > 80 and dist < 160:
            set_lod_level(3)


        if water.hovered:
            cursor.position = mouse.world_point
            grid_x = mouse.point[0] + .5
            grid_z = mouse.point[2] + .5
            grid_x *= current_terrain.model.width
            grid_z *= current_terrain.model.depth

            grid_x = int(grid_x)
            grid_z = int(grid_z)

            if grid_x < 0 or grid_x > current_terrain.model.width or grid_z < 0 or grid_z > current_terrain.model.depth:
                return  # outside

            cursor.y = current_terrain.model.height_values[grid_x][grid_z] * current_terrain.scale_y




    app.run()
