import sys
from copy import deepcopy
from math import floor

import pyperclip
from PIL import Image

from ursina import *
from ursina.array_tools import Array2D, enumerate_2d
from ursina.scripts.property_generator import generate_properties_for_class
from ursina.shaders import unlit_shader


@generate_properties_for_class()
class GridEditor(Entity):
    def __init__(self, size=(32,32), palette=(' ', '#', '|', 'o'), canvas_color=color.white, edit_mode=True, **kwargs):
        super().__init__(parent=camera.ui, position=(-.45,-.45), scale=.9, model='quad', origin=(-.5,-.5), visible_self=False)
        self.w, self.h = int(size[0]), int(size[1])
        self.canvas = Entity(parent=self, model='quad', origin=(-.5,-.5), shader=unlit_shader, scale=(self.w/self.h, 1), color=canvas_color)
        self.canvas_collider = Entity(parent=self.canvas, model='wireframe_quad', origin=self.canvas.origin, color=color.blue, scale=2, position=(-.5,-.5), collider='box', visible=False)
        sys.setrecursionlimit(max(sys.getrecursionlimit(), self.w * self.h))
        # self.grid = [[palette[0] for x in range(self.w)] for y in range(self.h)]
        if not hasattr(self, 'grid'):
            self.grid = Array2D(self.w, self.h, default_value=palette[0])
        self.brush_size = 1
        self.auto_render = True

        self.gizmo_parent = Entity(parent=self.canvas, scale=(1/self.w, 1/self.h))
        self.cursor = Entity(parent=self.gizmo_parent)
        self.cursor_graphics = Entity(parent=self.cursor, model=Quad(segments=0, mode='line', thickness=2), origin=(-.5,-.5), color=hsv(120,1,1,.5), z=-.02, shader=unlit_shader)

        self.selected_char = palette[1]
        self.palette = palette
        self.start_pos = None
        self.prev_draw = None
        self.lock_axis = None
        self.outline = Entity(parent=self.canvas, model=Quad(segments=0, mode='line', thickness=2), color=color.cyan, z=.01, origin=(-.5,-.5))

        self.selection_renderer = Entity(parent=self.gizmo_parent, model=Mesh(mode='line', thickness=2), color=color.lime, alpha=.5, z=-.01, origin=(-.5,-.5))
        self.rect_selection = [Vec2(0,0), Vec2(0,0)]
        self.rect_tool = Entity(parent=self.gizmo_parent, model=Quad(0, mode='line', thickness=2), color=color.cyan, z=-.01, origin=(-.5,-.5), start=Vec2(0,0), end=Vec2(0,0), enabled=False)
        # self.selection_mover = Draggable(parent=self.canvas, model='circle', color=color.blue, origin=(.5,.5), step=(1/self.w,1/self.h,0), enabled=False)
        self.selection_matrix = [[0 for y in range(self.h)] for x in range(self.w)]
        self.temp_paste_layer = Entity(parent=self.cursor, model='quad', origin=(-.5,-.5), z=-.02, enabled=False)
        Entity(parent=self.temp_paste_layer, model='wireframe_quad', origin=self.temp_paste_layer.origin, color=color.black)
        self.is_in_paste_mode = False

        self.undo_stack = []
        self.undo_stack.append(deepcopy(self.grid))
        self.undo_index = 0

        self.shortcuts = {
            'draw': 'left mouse',
            'sample_modifier': 'alt',
            'lock_axis_modifier': 'shift',
            'draw_line_modifier': 'control',
            'toggle_edit_mode': ('tab', ),
            'increase_brush_size': ('d', '+'),
            'decrease_brush_size': ('x', '-'),
            'save': ('control+s', ),
            'fill': ('g', ),
            'replace': ('shift+g', ),
            'undo': ('control+z', ),
            'redo': ('control+y', 'control+shift+z'),
            'flip_horizontally': ('f4', ),
            'select': 'right mouse',
            'subtract_selection_modifier': 'alt',
            'add_selection_modifier': 'shift',
            'copy': ('control+c', ),
            'cut': ('control+x', ),
            'paste': ('control+v', ),
            'apply_pasted': ('left mouse down', ),
            'discard_pasted': ('right mouse down', ),
            'flip_pasted_horizontally': ('f', ),
        }

        self.help_icon = Button(parent=self.canvas, scale=.025, model='circle', origin=(-.5,-.5), position=(-.0,1.005,-1), text='?', target_scale=.025)

        self.help_icon.tooltip = Tooltip(
            text='\n'.join([f'{key:<20}: {value}' for key, value in self.shortcuts.items()]),
            font='VeraMono.ttf',
            wordwrap=100,
            # scale=.75,
            )
        self.edit_mode = edit_mode

        for key, value in kwargs.items():
            setattr(self, key ,value)


    def palette_setter(self, value):
        self._palette = value
        if hasattr(self, 'palette_parent'):
            destroy(self.palette_parent)

        self.palette_parent = Entity(parent=self, position=(-.3,.5,-1), shader=unlit_shader)
        for i, e in enumerate(value):
            button_text = ''
            if isinstance(e, str):
                button_text = e

            b = Button(parent=self.palette_parent, scale=.05, text=button_text, model='quad', color=color._32, shader=unlit_shader)
            b.on_click = Func(setattr, self, 'selected_char', e)
            b.tooltip = Tooltip(str(e))

            if isinstance(e, Color):
                b.color = e

        grid_layout(self.palette_parent.children, max_x=4)

    def edit_mode_getter(self):
        return getattr(self, '_edit_mode', True)

    def edit_mode_setter(self, value):
        self._edit_mode = value
        self.cursor.enabled = value
        self.outline.enabled = value
        self.palette_parent.enabled = value


    def update(self):
        if not self.edit_mode:
            return

        self.cursor.enabled = self.canvas_collider.hovered
        if self.canvas_collider.hovered:
            self.cursor.position = mouse.point*2 - Vec3(.5,.5,0)

            # center cursor
            self.cursor.x -= self.brush_size // 2 / self.w
            self.cursor.y -= self.brush_size // 2 / self.h

            self.cursor.x = floor(self.cursor.x * self.w)
            self.cursor.y = floor(self.cursor.y * self.h)


            if self.start_pos is not None and held_keys[self.shortcuts['draw']]:
                if held_keys[self.shortcuts['lock_axis_modifier']] and self.prev_draw:
                    if not self.lock_axis:
                        if abs(mouse.velocity[0]) > abs(mouse.velocity[1]):
                            self.lock_axis = 'horizontal'
                        else:
                            self.lock_axis = 'vertical'

                    if self.lock_axis == 'horizontal':
                        self.cursor.y = self.prev_draw[1]

                    if self.lock_axis == 'vertical':
                        self.cursor.x = self.prev_draw[0]


                y = int(round(self.cursor.y))
                x = int(round(self.cursor.x))

                if not held_keys[self.shortcuts['sample_modifier']] and not self.is_in_paste_mode:
                    if self.prev_draw is not None and distance_2d(self.prev_draw, (x,y)) > 1:
                        dist = distance_2d(self.prev_draw, (x,y))

                        if dist > 1: # draw line
                            diff_x = x - self.prev_draw[0]
                            diff_y = y - self.prev_draw[1]

                            if abs(diff_x) != abs(diff_y):
                                for i in range(int(dist)+1):
                                    inbetween_pos = lerp(self.prev_draw, (x,y), i/dist)
                                    self.draw(int(inbetween_pos[0]), int(inbetween_pos[1]))
                            else:   # draw perfectly diagonal line
                                if diff_x > 0 and diff_y > 0:   # /
                                    for i in range(abs(diff_x)):
                                        self.draw(int(self.prev_draw[0]+i), int(self.prev_draw[1]+i))
                                elif diff_x > 0 and diff_y < 0: # \
                                    for i in range(abs(diff_x)):
                                        self.draw(int(self.prev_draw[0]+i), int(self.prev_draw[1]-i))
                                elif diff_x < 0 and diff_y < 0: # /
                                    for i in range(abs(diff_x)):
                                        self.draw(int(self.prev_draw[0]-i), int(self.prev_draw[1]-i))
                                elif diff_x < 0 and diff_y > 0: # \
                                    for i in range(abs(diff_x)):
                                        self.draw(int(self.prev_draw[0]-i), int(self.prev_draw[1]+i))


                            self.draw(x, y)
                            self.prev_draw = (x,y)

                    else:
                        self.draw(x, y)
                        self.prev_draw = (x,y)

                else:   # sample color
                    self.sample(x, y)


        if held_keys[self.shortcuts['select']]:     # selection
            self.rect_selection[1] = self.get_cursor_position()
            if self.rect_selection[0] == self.rect_selection[1]:
                self.rect_tool.start = Vec2(0,0)
                self.rect_tool.end = Vec2(0,0)
                self.rect_tool.enabled = False
                return

            self.rect_tool.start = Vec2(min(self.rect_selection[0].x, self.rect_selection[1].x), min(self.rect_selection[0].y, self.rect_selection[1].y))
            self.rect_tool.end =   Vec2(max(self.rect_selection[0].x, self.rect_selection[1].x)+1, max(self.rect_selection[0].y, self.rect_selection[1].y)+1)
            self.rect_tool.start.x = clamp(self.rect_tool.start.x, 0, self.w)
            self.rect_tool.start.y = clamp(self.rect_tool.start.y, 0, self.h)
            self.rect_tool.end.x = clamp(self.rect_tool.end.x, 0, self.w)
            self.rect_tool.end.y = clamp(self.rect_tool.end.y, 0, self.h)
            self.rect_tool.enabled = True
            self.rect_tool.position = self.rect_tool.start
            self.rect_tool.scale = (self.rect_tool.end - self.rect_tool.start)


        if hasattr(self, 'line_preview'):
            self.line_preview.enabled = held_keys['control']
        if held_keys[self.shortcuts['draw_line_modifier']] and self.prev_draw:
            if not hasattr(self, 'line_preview'):
                self.line_preview = Entity(parent=self.gizmo_parent, model=Mesh(mode='line', vertices=[Vec3.zero, Vec3.up], thickness=3), color=color.azure, z=-.1)

            self.line_preview.position = Vec2(*self.prev_draw)
            self.line_preview.look_at_2d(self.cursor)
            self.line_preview.scale_y = distance_2d(self.line_preview, self.cursor)


    def get_cursor_position(self):
        y = int(round(self.cursor.y))
        x = int(round(self.cursor.x))
        return Vec2(x,y)


    def draw(self, x, y):
        for _y in range(y, y + self.brush_size):
            for _x in range(x, x + self.brush_size):
                self.grid.set(_x, _y, self.selected_char)

        if self.auto_render:
            self.render()


    def render(self):
        print_warning('render() not implemented. GridEditor is a base class you can inherit, but doesn\'t implement a render function itself.')


    def sample(self, x, y):
        self.selected_char = self.grid[x][y]


    def input(self, key):
        combined_key = input_handler.get_combined_key(key)

        if key in self.shortcuts['toggle_edit_mode']:
            self.edit_mode = not self.edit_mode

        if not self.edit_mode:
            return

        if key in self.shortcuts['apply_pasted'] and self.is_in_paste_mode:
            self.paste()
            return  # prevent drawing right after pasting if draw and apply_pasted keys are the same

        if key in self.shortcuts['discard_pasted'] and self.is_in_paste_mode:
            self.paste(discard=True)


        if (key == self.shortcuts['draw']+' down' or key == self.shortcuts['draw']) and self.canvas_collider.hovered and not self.is_in_paste_mode:
            self.start_pos = self.get_cursor_position()
            if not held_keys[self.shortcuts['draw_line_modifier']]:
                self.prev_draw = None

        if key == self.shortcuts['draw']+' up' and self.start_pos:
            self.start_pos = None
            self.lock_axis = None
            self.render()

            if not held_keys[self.shortcuts['draw_line_modifier']]: # only record undo after all connected lines has been drawn, not each segment
                self.record_undo()

        if key in (self.shortcuts['select']+' down', self.shortcuts['select']) and not self.is_in_paste_mode:
            if not held_keys[self.shortcuts['add_selection_modifier']] and not held_keys[self.shortcuts['subtract_selection_modifier']]:
                self.selection_mode = 'overwrite'
                self.clear_selection()
            elif held_keys[self.shortcuts['add_selection_modifier']] and not held_keys[self.shortcuts['subtract_selection_modifier']]:
                self.selection_mode = 'add'
            elif held_keys[self.shortcuts['subtract_selection_modifier']] and not held_keys[self.shortcuts['add_selection_modifier']]:
                self.selection_mode = 'subtract'

            self.rect_selection[0] = self.get_cursor_position()

        if key == self.shortcuts['select']+' up':
            self.rect_tool.enabled = False

            new_value = int(self.selection_mode == 'overwrite' or self.selection_mode == 'add')
            for y in range(self.rect_tool.start.Y, self.rect_tool.end.Y):
                for x in range(self.rect_tool.start.X, self.rect_tool.end.X):
                    self.selection_matrix[x][y] = new_value

            self.render_selection()


        elif key in self.shortcuts['lock_axis_modifier']+' up':
            self._lock_origin = None

        elif combined_key in self.shortcuts['undo']:
            self.undo()

        elif combined_key in self.shortcuts['redo']:
            self.redo()

        elif combined_key in self.shortcuts['fill'] and self.canvas_collider.hovered:
            self.floodfill(self.grid, self.cursor.X, self.cursor.Y)
            self.render()
            self.record_undo()

        elif combined_key in self.shortcuts['replace'] and self.canvas_collider.hovered:
            value_to_replace = self.grid[self.cursor.X][self.cursor.Y]
            for (x,y), value in enumerate_2d(self.grid):
                if value == value_to_replace:
                    self.grid[x][y] = self.selected_char

            self.render()
            self.record_undo()

        elif combined_key in self.shortcuts['decrease_brush_size'] and self.brush_size > 1:
            self.brush_size -= 1
            self.cursor_graphics.scale = self.brush_size
            self.prev_draw = None

        elif combined_key in self.shortcuts['increase_brush_size'] and self.brush_size <  8:
            self.brush_size += 1
            self.cursor_graphics.scale = self.brush_size
            self.prev_draw = None

        if combined_key in self.shortcuts['save']:
            print('saved:', self.canvas.texture.path)
            if hasattr(self, 'save'):
                self.save()

        elif combined_key in self.shortcuts['copy']:
            self.copy()

        elif combined_key in self.shortcuts['cut']:
            self.cut()

        elif combined_key in self.shortcuts['paste']:
            self.enter_paste_mode()

        elif self.is_in_paste_mode and combined_key in self.shortcuts['flip_pasted_horizontally']:
            # for (x,y), colr in enumerate(self.pastedata):
            #     self.paste_data[x][y] = self.paste_data[][]
            self.paste_data = Array2D(data=self.paste_data[::-1])
            self.update_paste_texture()

        elif combined_key in self.shortcuts['flip_horizontally']:
            self.flip_horizontally()


    def undo(self):
        self.undo_index -= 1
        self.undo_index = clamp(self.undo_index, 0, len(self.undo_stack)-1)
        self.grid = deepcopy(self.undo_stack[self.undo_index])
        self.render()

    def redo(self):
        self.undo_index += 1
        self.undo_index = clamp(self.undo_index, 0, len(self.undo_stack)-1)
        self.grid = deepcopy(self.undo_stack[self.undo_index])
        self.render()

    def record_undo(self):
        self.undo_index += 1
        self.undo_stack = self.undo_stack[:self.undo_index]
        self.undo_stack.append(deepcopy(self.grid))
        # print('-----', self.undo_index, len(self.undo_stack))


    def floodfill(self, matrix, x, y, first=True):
        if matrix.get(x, y, default=self.selected_char) == self.selected_char:
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

    def copy(self):
        # crop matrix
        # find the indices of the rows and columns with True values
        rows = [i for i in range(len(self.selection_matrix)) if any(self.selection_matrix[i])]
        cols = [j for j in range(len(self.selection_matrix[0])) if any(self.selection_matrix[i][j] for i in range(len(self.selection_matrix)))]
        if not rows or not cols:
            return
        # crop the matrix based on the boolean values
        start_x = min(rows)
        start_y = min(cols)
        # end_x = max(rows) + 1
        # end_y = max(cols) + 1
        selection_width =  (max(rows) + 1) - start_x
        selection_height = (max(cols) + 1) - start_y
        # cropped_matrix = [[matrix[i][j] for j in range(start_y, max(cols) + 1)] for i in range(start_x, max(rows) + 1)]

        copy_data = [[tuple(self.grid[start_x+x][start_y+y]) if self.selection_matrix[start_x+x][start_y+y] else None for y in range(selection_height)] for x in range(selection_width)]

        copy_data = self.grid.get_area(Vec2(start_x, start_y).XY, Vec2(start_x+selection_width, start_y+selection_height).XY)
        # pyperclip.copy(json.dumps(dict(data=copy_data)))
        for (x,y), colr in enumerate_2d(copy_data):
            copy_data[x][y] = color.rgb_to_hex(*colr)

        pyperclip.copy(copy_data.to_string())
        print('copied:', copy_data.to_string())

    def cut(self):
        self.copy()
        for x in range(len(self.selection_matrix)):
            for y in range(len(self.selection_matrix[0])):
                if self.selection_matrix[x][y]:
                    self.grid[x][y] = color.white
        self.render()


    def enter_paste_mode(self):
        self.is_in_paste_mode = True
        self.paste_data = pyperclip.paste()
        if not self.paste_data:
            print("trying to paste, but there's nothing on the clipboard")
            return
        try:
            self.paste_data = Array2D.from_string(self.paste_data, convert_to_type=str)
            for (x,y), hex_code in enumerate_2d(self.paste_data):
                self.paste_data[x][y] = color.hex(hex_code)

        except Exception as e:
            self.paste_data = None
            print_warning('error parsing paste data as json:', self.paste_data, e)
            return

        w = self.paste_data.width
        h = self.paste_data.height

        self.temp_paste_layer.enabled = True
        self.temp_paste_layer.scale = (w, h)

        if not self.temp_paste_layer.texture or self.temp_paste_layer.texture.size != (w,h):
            self.temp_paste_layer.texture = Texture(Image.new(mode='RGBA', size=(w,h), color=(0,0,0,0)))
        self.update_paste_texture()


    def update_paste_texture(self):
        for (x,y), colr in enumerate_2d(self.paste_data):
            self.temp_paste_layer.texture.set_pixel(x, y, colr)
        self.temp_paste_layer.texture.apply()


    def paste(self, discard=False, record_undo=True):
        self.is_in_paste_mode = False
        self.temp_paste_layer.enabled = False
        if discard:
            return

        self.grid.paste(self.paste_data, self.cursor.X, self.cursor.Y, ignore=color.clear)

        self.clear_selection()
        self.render()


    def flip_horizontally(self):
        self.grid = self.grid[::-1]
        self.render()


    def clear_selection(self):
        self.selection_matrix = [[0 for y in range(self.h)] for x in range(self.w)]
        self.selection_renderer.model.clear()
        print('clear selection')


    def render_selection(self):
        self.selection_renderer.model.clear(False)
        verts = []
        for x in range(self.w):
            for y in range(self.h):
                if self.selection_matrix[x][y]:
                    if x <= 0 or not self.selection_matrix[x-1][y]:
                        verts.extend((Vec3(x,y,0), Vec3(x,y+1,0)))
                    if x >= self.w-1 or not self.selection_matrix[x+1][y]:
                        verts.extend((Vec3(x+1,y,0), Vec3(x+1,y+1,0)))
                    if y <= 0 or not self.selection_matrix[x][y-1]:
                        verts.extend((Vec3(x,y,0), Vec3(x+1,y,0)))
                    if y >= self.h-1 or not self.selection_matrix[x][y+1]:
                        verts.extend((Vec3(x,y+1,0), Vec3(x+1,y+1,0)))

        self.selection_renderer.model.vertices = [v+Vec3(-.5,-.5,0) for v in verts]
        self.selection_renderer.model.triangles = [(i, i+1) for i in range(0, len(verts), 2)]
        self.selection_renderer.model.generate()


class PixelEditor(GridEditor):
    def __init__(self, texture, palette=(color.black, color.white, color.light_gray, color.gray, color.red, color.orange, color.yellow, color.lime, color.green, color.turquoise, color.cyan, color.azure, color.blue, color.violet, color.magenta, color.pink), **kwargs):
        super().__init__(texture=texture, size=texture.size, palette=palette, **kwargs)
        self.set_texture(texture)

    def set_texture(self, texture, render=True, clear_undo_stack=True):
        self.canvas.texture = texture
        self.w, self.h = int(texture.width), int(texture.height)
        self.canvas.scale_x = self.canvas.scale_y * self.w / self.h

        # pixels = texture.pixels
        self.grid = Array2D(width=texture.width, height=texture.height)
        for (x,y), _ in enumerate_2d(self.grid):
            self.grid[x][y] = texture.get_pixel(x,y)
        self.canvas.texture.filtering = None

        self.gizmo_parent.scale = Vec2(1/self.w, 1/self.h)
        self.help_icon.scale = self.help_icon.target_scale
        self.clear_selection()

        if clear_undo_stack:
            self.undo_stack.clear()
            self.record_undo()
            self.undo_index = 0

        if render:
            self.render()


    def draw(self, x, y):
        for _y in range(max(y,0), min(y+self.brush_size, self.h)):
            for _x in range(max(x,0), min(x+self.brush_size, self.w)):
                self.grid[_x][_y] = self.selected_char
                self.canvas.texture.set_pixel(_x, _y, self.grid[_x][_y])

        self.canvas.texture.apply()


    def render(self):
        for (x,y), value in enumerate_2d(self.grid):
            self.canvas.texture.set_pixel(x, y, value)

        self.canvas.texture.apply()


    def save(self):
        if self.canvas.texture.path:
            self.canvas.texture.save(self.canvas.texture.path)
            # print('saved:', self.canvas.texture.path)

    @property
    def texture(self):
        if not hasattr(self, 'canvas'):
            return None
        return self.canvas.texture

    @texture.setter
    def texture(self, value):
        if hasattr(self, 'canvas'):
            self.canvas.texture = value



if __name__ == '__main__':
    app = Ursina()
    '''
    pixel editor example, it's basically a drawing tool.
    can be useful for level editors and such
    here we create a new texture, but can also give it an existing texture to modify.
    '''
    from PIL import Image
    t = Texture(Image.new(mode='RGBA', size=(32,32), color=(0,0,0,1)))
    editor = PixelEditor(parent=scene, texture=load_texture('test_tileset'), scale=10)
    camera.orthographic = True
    camera.fov = 15
    EditorCamera(rotation_speed=0)


    app.run()
