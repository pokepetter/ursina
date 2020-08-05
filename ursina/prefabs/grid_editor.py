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
        self.grid = [[palette[0] for x in range(self.w)] for y in range(self.h)]
        self.brush_size = 1
        self.cursor = Entity(parent=self, model=Quad(segments=0, mode='line'), origin=(-.5,-.5), scale=(1/self.w, 1/self.h), color=color.color(0,1,1,.2), z=-.1)

        self.selected_char = palette[1]
        self.palette = palette
        self.prev_draw = None
        self.start_pos = (0,0)

        self.undo_cache = list()
        self.undo_cache.append(deepcopy(self.grid))
        self.undo_index = 0

        self.help_text = Text(
            text=dedent('''
                left mouse:    draw
                control(hold): draw lines
                alt(hold):     select character
                ctrl + z:      undo
                ctrl + y:      redo
            '''),
            position=window.top_left,
            scale=.75
            )

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

        self.palette_parent = Entity(parent=camera.ui, position=(-.75,-.05))
        for i, e in enumerate(value):
            if isinstance(e, str):
                i = e

            b = Button(parent=self.palette_parent, scale=.05, text=i, model='quad', color=color._32)
            b.on_click = Func(setattr, self, 'selected_char', e)
            b.tooltip = Tooltip(str(e))

            if isinstance(e, Color):
                b.color = e

        grid_layout(self.palette_parent.children, max_x=4)




    def update(self):
        self.cursor.enabled = mouse.hovered_entity == self
        if self.hovered:
            self.cursor.position = mouse.point
            self.cursor.x = floor(self.cursor.x * self.w) / self.w
            self.cursor.y = floor(self.cursor.y * self.h) / self.h

            if mouse.left:
                y = int(round(self.cursor.y * self.h))
                x = int(round(self.cursor.x * self.w))

                if not held_keys['alt']:
                    if self.prev_draw is not None and distance2d(self.prev_draw, (x,y)) > 1:
                        dist = distance2d(self.prev_draw, (x,y))

                        if dist > 1: # draw line
                            for i in range(int(dist)):
                                inbetween_pos = lerp(self.prev_draw, (x,y), i/dist)
                                self.draw(int(inbetween_pos[0]), int(inbetween_pos[1]))

                            self.draw(x, y)
                            self.prev_draw = (x,y)

                    else:
                        self.draw(x, y)
                        self.prev_draw = (x,y)

                else:
                    self.selected_char = self.grid[y][x]



    def draw(self, x, y):
        for _y in range(y, min(y+self.brush_size, self.h)):
            for _x in range(x, min(x+self.brush_size, self.w)):
                self.grid[_y][_x] = self.selected_char

        self.render()


    def input(self, key):
        if key == 'left mouse down':
            self.start_pos = (
                int(self.cursor.x * (self.w+1)),
                -int(self.cursor.y * self.h)
            )
            if not held_keys['control']:
                self.prev_draw = None

        if key == 'left mouse up' and not held_keys['control']:
            self.undo_index += 1
            self.undo_cache = self.undo_cache[:self.undo_index]
            self.undo_cache.append(deepcopy(self.grid))


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
            self.undo_index += 1
            self.undo_cache = self.undo_cache[:self.undo_index]
            self.undo_cache.append(deepcopy(self.grid))

        if key == 'x' and self.brush_size > 1:
            self.brush_size -= 1
            self.cursor.scale = Vec2(self.brush_size / self.w, self.brush_size / self.h)

        if key == 'd' and self.brush_size <  8:
            self.brush_size += 1
            self.cursor.scale = Vec2(self.brush_size / self.w, self.brush_size / self.h)


    def floodfill(self, matrix, x, y, first=True):
        if matrix[y][x] == self.selected_char:
            return

        if first:
            self.fill_target = matrix[y][x]

        if matrix[y][x] == self.fill_target:
            matrix[y][x] = self.selected_char
            # recursively invoke flood fill on all surrounding cells
            if x > 0:
                self.floodfill(matrix, x-1, y, first=False)
            if x < self.w-1:
                self.floodfill(matrix, x+1, y, first=False)
            if y > 0:
                self.floodfill(matrix, x, y-1, first=False)
            if y < self.h-1:
                self.floodfill(matrix, x, y+1, first=False)



def PixelEditor(texture, palette=(color.black, color.white, color.light_gray, color.gray, color.red, color.orange, color.yellow, color.lime,
        color.green, color.turquoise, color.cyan,       color.azure,
        color.blue,  color.violet,    color.magenta,    color.pink
        )):
    grid_editor = GridEditor(texture=texture, size=texture.size, palette=palette)
    grid_editor.texture.filtering = False
    def render_grid_as_image():
        for y in range(grid_editor.h):
            for x in range(grid_editor.w):
                t.set_pixel(x, y, grid_editor.grid[y][x])

        texture.apply()

    grid_editor.render = render_grid_as_image
    grid_editor.render()
    return grid_editor


def ASCIIEditor(size=(61,28), palette=(' ', '#', '|', 'A', '/', '\\', 'o', '_', '-', 'i', 'M', '.'), font='VeraMono.ttf'):
    grid_editor = GridEditor(size=size, palette=palette, color=color.black)
    grid_editor.text_entity = Text(text='', position=(-.45,-.45,-2), line_height=1.1, origin=(-.5,-.5), font=font)
    grid_editor.scale = (Text.get_width(' '*grid_editor.w), grid_editor.h*Text.size*grid_editor.text_entity.line_height)

    def render_grid_as_text():
        grid_editor.text_entity.text = '\n'.join([''.join(line) for line in reversed(grid_editor.grid)])

    # if held_keys['control'] and key == 'c':
    #     pyperclip.copy(t.text)
    #
    # if held_keys['control'] and key == 'v' and pyperclip.paste().count('\n') == (h-1):
    #     t.text = pyperclip.paste()
    #     undo_index += 1
    #     undo_cache = undo_cache[:undo_index]
    #     undo_cache.append(deepcopy(grid))

    grid_editor.render = render_grid_as_text
    grid_editor.render()
    return grid_editor



if __name__ == '__main__':
    app = Ursina()
    # window.color = color.black
    Text.default_font = 'VeraMono.ttf'



    from PIL import Image
    t = Texture(Image.new(mode='RGBA', size=(32,32), color=(0,0,0,1)))
    PixelEditor(t)

    # ASCIIEditor()

    def input(key):
        if key == '-':
            grid_editor.scale *= .95

    app.run()
