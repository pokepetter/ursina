from ursina import *
from ursina.prefabs.grid_editor import GridEditor, PixelEditor
import re

class Tilemap(GridEditor):
    def __init__(self, tilemap='', tileset='', tileset_size=(8,8), **kwargs):
        if isinstance(tilemap, str):
            self.tilemap = load_texture(tilemap)

        self.grid = [[self.tilemap.get_pixel(x,y) for y in range(self.tilemap.height)] for x in range(self.tilemap.width)]
        super().__init__(
            texture=self.tilemap,
            size=self.tilemap.size,
            palette=(color.white, color.black, color.green, color.blue, color.red),
            edit_mode=False,
            **kwargs)

        self.tileset = tileset
        self.tileset_size = tileset_size
        self.model = Mesh()
        self.texture = tileset
        self.colliders = list()
        # self.texture.filtering = None

        # self.grid = [[self.tilemap.get_pixel(x,y) for y in range(self.h)] for x in range(self.w)]
        self.auto_render = False
        self.outline = Entity(parent=self, model=Quad(segments=0, mode='line', thickness=1), color=color.cyan, z=.01, origin=(-.5,-.5), enabled=self.edit_mode)

        self._quad = Quad(segments=0)
        self._quad.vertices = [Vec3(*v)+Vec3(.5,.5,0) for v in self._quad.vertices]
        self._garbage = Entity(parent=self, add_to_scene_entities=False)

        self.uv_dict = {
            '11111111' : [(4,1), (5,1), (6,1), (7,1)],     # fill

            '0.11111.' : [(1,3), (2,3), (5,3), (6,3)],     # top
            '1.0.1111' : [(3,2), (3,1)],     # right
            '111.0.11' : [(2,0), (1,0), (6,2), (5,2)],     # bot
            '11111.0.' : [(0,1), (0,2)],     # left

            '000.111.' : [(3,3), ],     # corner_top_right
            '1.000.11' : [(3,0), ],     # corner_bot_right
            '111.000.' : [(0,0), ],     # corner_bot_left
            '0.111.00' : [(0,3), ],     # corner_top_left

            '10111111' : [(1,1), ],     #inner_corner_bot_left
            '11101111' : [(1,2), ],     #inner_corner_top_left
            '11111011' : [(2,2), ],     #inner_corner_top_right
            '11111110' : [(2,1), ],     #inner_corner_bot_right

        }
        self.single_block_coordinates = [(4,0), (5,0), (6,0), (7,0)]
        self.variation_chance = [0,0,0,0,1,1,1,2,2,3]

        if 'min' in self.texture.name:
            self.uv_dict = {
                '11111111' : [(1,1)],     # fill

                '0.11111.' : [(1,2)],     # top
                '111.0.11' : [(1,0), ],     # bot
                '1.0.1111' : [(0,1), '-1,1'],     # right
                '11111.0.' : [(0,1)],     # left

                '0.111.00' : [(0,2), ],     # corner_top_left
                '000.111.' : [(0,2), '-1,1'],     # corner_top_right
                '1.000.11' : [(0,2), '-1,-1'],     # corner_bot_right
                '111.000.' : [(0,2), '1,-1'],     # corner_bot_left

                '11111110' : [(2,0), ],     #inner_corner_bot_right
                '10111111' : [(2,0), '-1,1'],     #inner_corner_bot_left
                '11111011' : [(2,1), ],     #inner_corner_top_right
                '11101111' : [(2,1), '-1,1'],     #inner_corner_top_left
            }
            self.single_block_coordinates = [(2,2)]
            self.variation_chance = [0,]

        self.uv_margin = .002

        self.render()


    def update(self):
        if not self.edit_mode:
            return

        super().update()
        if mouse.left:
            self.draw_temp(self.cursor.position)


    def draw_temp(self, position):
        e = Entity(
            parent=self._garbage,
            model='quad',
            scale=Vec3(1/self.tilemap.width, 1/self.tilemap.height, 1) * self.brush_size,
            position=self.cursor.position,
            z=-.1,
            texture=self.texture,

            texture_scale=Vec2(1/self.tileset_size[0], 1/self.tileset_size[1]),
            texture_offset=Vec2(.33, .33),
            origin=(-.5,-.5),
            ignore=True,
            )
        if self.selected_char == self.palette[0]:
            e.color = window.color
            e.texture = None




    def input(self, key):
        super().input(key)
        if key == 'left mouse up':
            for e in self._garbage.children:
                destroy(e)


    def render(self):
        self.scale = self.tilemap.size
        self.model.clear()

        for e in self.colliders:
            destroy(e)
        self.colliders.clear()

        tile_size = Vec2(1/self.tileset_size[0], 1/self.tileset_size[1])

        i = 0
        for y in range(self.tilemap.height):

            collider = None
            for x in range(self.tilemap.width):
                col = self.grid[x][y]

                if col == color.white and collider: # end collider
                    collider = None

                if col != color.white: #
                    self.model.vertices.extend([Vec3(x/self.tilemap.width, y/self.tilemap.height, 0) + (v*1/self.tilemap.width) for v in self._quad.vertices]) # add quad vertices, but offset.
                    self.model.triangles.append([i+j for j in range(4)])

                    neighbours = list()
                    # register neighbours clockwise starting from the top
                    for offset in [(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]:
                        try:
                            neighbours.append(self.grid[x+offset[0]][y+offset[1]] != color.white)
                        except IndexError:
                            neighbours.append(1)

                    neighbours = ''.join([str(int(e)) for e in neighbours])

                    # if collider is None and neighbours != '11111111':
                    #     collider = Entity(
                    #         parent=self,
                    #         model='cube',
                    #         scale_x=Vec3(0, 1/self.tilemap.height, 1),
                    #         origin_x=-.5,
                    #         position=(x-.5, y/self.tilemap.height),
                    #         collider='box',
                    #         color=color.red
                    #         )
                    #     self.colliders.append(collider)
                    # if collider and neighbours == '11111111': # end collider if it's a middle block
                    #     collider = None
                    # if collider:
                    #     collider.scale_x += 1/self.tilemap.width

                    random.seed(y+x)
                    variation_index = random.choice(self.variation_chance)
                    tile_scale = '1,1'

                    for key, value in self.uv_dict.items():
                        if re.match(key, neighbours):
                            if isinstance(value[-1], str):
                                tile_scale = value[-1]

                            variation_index = min(variation_index, len(value)-1-int(tile_scale=='1,1'))
                            _x, _y = value[variation_index]
                            break
                        else:
                            _x, _y = self.single_block_coordinates[variation_index]

                    uv = [
                        Vec2(tile_size[0] * _x,     tile_size[1] * _y)     + Vec2(self.uv_margin, self.uv_margin),
                        Vec2(tile_size[0] * (_x+1), tile_size[1] * _y)     + Vec2(-self.uv_margin, self.uv_margin),
                        Vec2(tile_size[0] * (_x+1), tile_size[1] * (_y+1)) + Vec2(-self.uv_margin, -self.uv_margin),
                        Vec2(tile_size[0] * _x,     tile_size[1] * (_y+1)) + Vec2(self.uv_margin, -self.uv_margin),
                    ]
                    if tile_scale == '1,1':
                        pass
                    elif tile_scale == '-1,1':
                        a, b, c, d = uv
                        uv = [b, a, d, c]
                    elif tile_scale == '1,-1':
                        a, b, c, d = uv
                        uv = [d, c, b, a]
                    elif tile_scale == '-1,-1':
                        a, b, c, d = uv
                        uv = [c, d, a, b]


                    self.model.uvs.extend(uv)
                    i += 4


        self.model.generate() # call to create the mesh


    def save(self):
        for y in range(self.tilemap.height):
            for x in range(self.tilemap.width):
                self.tilemap.set_pixel(x, y, self.grid[x][y])

        if self.tilemap.path:
            self.tilemap.save(self.tilemap.path)
            print('saving:', self.tilemap.path)



if __name__ == '__main__':
    app = Ursina()
    EditorCamera()
    tilemap = Tilemap('tilemap_test_level', tileset='test_tileset', tileset_size=(8,4), parent=scene)
    # tilemap = Tilemap('brick', tileset='tileset_cave', tileset_size=(8,4), parent=scene)
    camera.orthographic = True
    camera.position = tilemap.tilemap.size / 2
    camera.fov = tilemap.tilemap.height

    Text('press tab to toggle edit mode', origin=(.5,0), position=(-.55,.4))

    app.run()
