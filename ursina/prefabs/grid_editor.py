from ursina import *
import pyperclip
from copy import deepcopy
import sys
from math import floor



class GridEditor(Entity):
    def __init__(self, size=(32,32), palette=(' ', '#', '|', 'o'), **kwargs):
        super().__init__(parent=camera.ui, model='quad', position=(-.45,-.45), origin=(-.5,-.5), scale=.9, collider='box')

        self.w, self.h = int(size[0]), int(size[1])
        sys.setrecursionlimit(self.w * self.h)
        # self.grid = [[palette[0] for x in range(self.w)] for y in range(self.h)]
        if not hasattr(self, 'grid'):
            self.grid = [[palette[0] for y in range(self.h)] for x in range(self.w)]
        self.brush_size = 1
        self.auto_render = True
        self.cursor = Entity(parent=self, model=Quad(segments=0, mode='line', thickness=2), origin=(-.5,-.5), scale=(1/self.w, 1/self.h), color=color.color(120,1,1,.5), z=-.2)

        self.selected_char = palette[1]
        self.palette = palette
        self.prev_draw = None
        self.lock_axis = None
        self.outline = Entity(parent=self, model=Quad(segments=0, mode='line', thickness=2), color=color.cyan, z=.01, origin=(-.5,-.5))

        self.undo_cache = list()
        self.undo_cache.append(deepcopy(self.grid))
        self.undo_index = 0

        self.help_text = Text(
            text=dedent('''
                left mouse:    draw
                control(hold): draw lines
                alt(hold):     select character
                right click:   select character
                ctrl + z:      undo
                ctrl + y:      redo
            '''),
            position=window.top_left,
            scale=.75
            )

        self.edit_mode = True

        for key, value in kwargs.items():
            setattr(self, key ,value)



    @property
    def palette(self):
        return self._palette

    @palette.setter
    def palette(self, value):
        self._palette = value
        if hasattr(self, 'palette_parent'):
            destroy(self.palette_parent)

        self.palette_parent = Entity(parent=self, position=(-.3,.5))
        for i, e in enumerate(value):
            if isinstance(e, str):
                i = e

            b = Button(parent=self.palette_parent, scale=.05, text=i, model='quad', color=color._32)
            b.on_click = Func(setattr, self, 'selected_char', e)
            b.tooltip = Tooltip(str(e))

            if isinstance(e, Color):
                b.color = e

        grid_layout(self.palette_parent.children, max_x=4)


    @property
    def edit_mode(self):
        return self._edit_mode

    @edit_mode.setter
    def edit_mode(self, value):
        self._edit_mode = value
        self.cursor.enabled = value
        self.outline.enabled = value
        self.palette_parent.enabled = value
        self.help_text.enabled = value


    def update(self):
        if not self.edit_mode:
            return

        self.cursor.enabled = mouse.hovered_entity == self
        if self.hovered:

            self.cursor.position = mouse.point
            self.cursor.x = floor(self.cursor.x * self.w) / self.w
            self.cursor.y = floor(self.cursor.y * self.h) / self.h

            if mouse.left or mouse.right:
                if held_keys['shift'] and self.prev_draw:
                    if not self.lock_axis:
                        if abs(mouse.velocity[0]) > abs(mouse.velocity[1]):
                            self.lock_axis = 'horizontal'
                        else:
                            self.lock_axis = 'vertical'

                    if self.lock_axis == 'horizontal':
                        self.cursor.y = self.prev_draw[1] / self.h

                    if self.lock_axis == 'vertical':
                        self.cursor.x = self.prev_draw[0] / self.w


                y = int(round(self.cursor.y * self.h))
                x = int(round(self.cursor.x * self.w))


                if not held_keys['alt'] and not mouse.right:
                    if self.prev_draw is not None and distance_2d(self.prev_draw, (x,y)) > 1:
                        dist = distance_2d(self.prev_draw, (x,y))

                        if dist > 1: # draw line
                            for i in range(int(dist)+1):
                                inbetween_pos = lerp(self.prev_draw, (x,y), i/dist)
                                self.draw(int(inbetween_pos[0]), int(inbetween_pos[1]))

                            self.draw(x, y)
                            self.prev_draw = (x,y)

                    else:
                        self.draw(x, y)
                        self.prev_draw = (x,y)

                else:
                    self.selected_char = self.grid[x][y]



    def draw(self, x, y):
        for _y in range(y, min(y+self.brush_size, self.h)):
            for _x in range(x, min(x+self.brush_size, self.w)):
                self.grid[_x][_y] = self.selected_char

        if self.auto_render:
            self.render()


    def input(self, key):
        if key == 'tab':
            self.edit_mode = not self.edit_mode

        if not self.edit_mode:
            return

        if key == 'left mouse down':
            self.start_pos = self.cursor.position
            if not held_keys['control']:
                self.prev_draw = None

        if key == 'left mouse up':
            self.start_pos = None
            self.lock_axis = None
            self.render()

            if not held_keys['control']:
                self.record_undo()

        if key == 'shift up':
            self._lock_origin = None

        if held_keys['control'] and key == 'z':
            self.undo_index -= 1
            self.undo_index = clamp(self.undo_index, 0, len(self.undo_cache)-1)
            self.grid = deepcopy(self.undo_cache[self.undo_index])
            self.render()

        if held_keys['control'] and key == 'y':
            self.undo_index += 1
            self.undo_index = clamp(self.undo_index, 0, len(self.undo_cache)-1)
            self.grid = deepcopy(self.undo_cache[self.undo_index])
            self.render()

        # fill
        if key == 'g':
            y = int(self.cursor.y * self.h)
            x = int(self.cursor.x * self.w)
            self.floodfill(self.grid, x, y)
            self.render()
            self.record_undo()

        if key == 'x' and self.brush_size > 1:
            self.brush_size -= 1
            self.cursor.scale = Vec2(self.brush_size / self.w, self.brush_size / self.h)
            self.prev_draw = None

        if key == 'd' and self.brush_size <  8:
            self.brush_size += 1
            self.cursor.scale = Vec2(self.brush_size / self.w, self.brush_size / self.h)
            self.prev_draw = None

        if held_keys['control'] and key == 's':
            if hasattr(self, 'save'):
                self.save()


    def record_undo(self):
        self.undo_index += 1
        self.undo_cache = self.undo_cache[:self.undo_index]
        self.undo_cache.append(deepcopy(self.grid))



    def floodfill(self, matrix, x, y, first=True):
        if matrix[x][y] == self.selected_char:
            return

        if first:
            self.fill_target = matrix[x][y]

        if matrix[x][y] == self.fill_target:
            matrix[x][y] = self.selected_char
            # recursively invoke flood fill on all surrounding cells
            if x > 0:
                self.floodfill(matrix, x-1, y, first=False)
            if x < self.w-1:
                self.floodfill(matrix, x+1, y, first=False)
            if y > 0:
                self.floodfill(matrix, x, y-1, first=False)
            if y < self.h-1:
                self.floodfill(matrix, x, y+1, first=False)




class PixelEditor(GridEditor):
    def __init__(self, texture, palette=(color.black, color.white, color.light_gray, color.gray, color.red, color.orange, color.yellow, color.lime, color.green, color.turquoise, color.cyan, color.azure, color.blue, color.violet, color.magenta, color.pink), **kwargs):
        self.grid = [[texture.get_pixel(x,y) for y in range(texture.height)] for x in range(texture.width)]
        super().__init__(texture=texture, size=texture.size, palette=palette, **kwargs)
        self.texture.filtering = False
        self.render()

    def draw(self, x, y):
        for _y in range(y, min(y+self.brush_size, self.h)):
            for _x in range(x, min(x+self.brush_size, self.w)):
                self.grid[_x][_y] = self.selected_char
                self.texture.set_pixel(_x, _y, self.grid[_x][_y])

        self.texture.apply()


    def render(self):
        for y in range(self.h):
            for x in range(self.w):
                self.texture.set_pixel(x, y, self.grid[x][y])

        self.texture.apply()


    def save(self):
        if self.texture.path:
            self.texture.save(self.texture.path)
            print('saving:', self.texture.path)



class ASCIIEditor(GridEditor):
    def __init__(self, size=(61,28), palette=(' ', '#', '|', 'A', '/', '\\', 'o', '_', '-', 'i', 'M', '.'), font='VeraMono.ttf', color=color.black, line_height=1.1, **kwargs):
        super().__init__(size=size, palette=palette, color=color, **kwargs)
        rotated_grid = list(zip(*self.grid[::-1]))
        text = '\n'.join([''.join(reversed(line)) for line in reversed(rotated_grid)])

        self.text_entity = Text(parent=self.parent, text=text, x=-.0, y=.5, line_height=line_height, font=font)

        self.scale = (self.text_entity.width, self.text_entity.height)
        self.text_entity.world_parent = self
        self.text_entity.y = 1
        self.text_entity.z = -.001

    def render(self):
        rotated_grid = list(zip(*self.grid[::-1]))
        self.text_entity.text = '\n'.join([''.join(reversed(line)) for line in reversed(rotated_grid)])


    def input(self, key):
        super().input(key)
        if held_keys['control'] and key == 'c':
            print(self.text_entity.text)
            pyperclip.copy(self.text_entity.text)
        #
        # if held_keys['control'] and key == 'v' and pyperclip.paste().count('\n') == (h-1):
        #     t.text = pyperclip.paste()
        #     undo_index += 1
        #     undo_cache = undo_cache[:undo_index]
        #     undo_cache.append(deepcopy(grid))




if __name__ == '__main__':
    app = Ursina(size=(1920,1080))
    '''
    pixel editor example, it's basically a drawing tool.
    can be useful for level editors and such
    here we create a new texture, but can also give it an existing texture to modify.
    '''
    from PIL import Image
    t = Texture(Image.new(mode='RGBA', size=(32,32), color=(0,0,0,1)))
    from ursina.prefabs.grid_editor import PixelEditor
    PixelEditor(texture=load_texture('brick'), x=-.7, scale=.6)

    '''
    same as the pixel editor, but with text.
    '''
    from ursina.prefabs.grid_editor import ASCIIEditor
    ASCIIEditor(x=0, scale=.1)

    app.run()
