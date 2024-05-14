from ursina import *
import pyperclip
from PIL import Image
from copy import deepcopy
import sys
from math import floor
from ursina.shaders import unlit_shader
import json


from ursina.scripts.property_generator import generate_properties_for_class
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
            self.grid = [[palette[0] for y in range(self.h)] for x in range(self.w)]
        self.brush_size = 1
        self.auto_render = True
        self.cursor = Entity(parent=self.canvas, model=Quad(segments=0, mode='line', thickness=2), origin=(-.5,-.5), scale=(1/self.w, 1/self.h), color=color.hsv(120,1,1,.5), z=-.2, shader=unlit_shader)

        self.selected_char = palette[1]
        self.palette = palette
        self.start_pos = None
        self.prev_draw = None
        self.lock_axis = None
        self.outline = Entity(parent=self.canvas, model=Quad(segments=0, mode='line', thickness=2), color=color.cyan, z=.01, origin=(-.5,-.5))

        self.rect_selection = [Vec2(0,0), Vec2(0,0)]
        self.selection_renderer = Entity(parent=self.canvas, model=Mesh(mode='line', thickness=2), color=color.lime, alpha=.5, z=-.01, origin=(-.5,-.5), scale=(1/self.w,1/self.h))
        self.rect_tool = Entity(parent=self.canvas, model=Quad(0, mode='line', thickness=2), color=color.lime, z=-.01, origin=(-.5,-.5), start=Vec2(0,0), end=Vec2(0,0))
        # self.selection_mover = Draggable(parent=self.canvas, model='circle', color=color.blue, origin=(.5,.5), step=(1/self.w,1/self.h,0), enabled=False)
        self.selection_matrix = [[0 for y in range(self.h)] for x in range(self.w)]
        self.temp_paste_layer = Entity(parent=self.cursor, model='quad', origin=(-.5,-.5), z=-.02, enabled=False)
        Entity(parent=self.temp_paste_layer, model='wireframe_quad', origin=self.temp_paste_layer.origin, color=color.black)
        self.is_in_paste_mode = False

        self.undo_stack = []
        self.undo_stack.append(deepcopy(self.grid))
        self.undo_index = 0

        self.help_icon = Button(parent=self.canvas, scale=.025, model='circle', origin=(-.5,-.5), position=(-.0,1.005,-1), text='?', target_scale=.025)
        self.help_icon.tooltip = Tooltip(
            text=dedent('''
                left mouse:    draw
                control(hold): draw lines
                alt(hold):     select character
                right click:   select character
                ctrl + z:      undo
                ctrl + y:      redo
            '''),
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

            self.cursor.x = floor(self.cursor.x * self.w) / self.w
            self.cursor.y = floor(self.cursor.y * self.h) / self.h


            if self.start_pos and mouse.left:
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
                if x < 0 or x > self.w-1 or y < 0 or y > self.h-1:
                    self.prev_draw = (clamp(x, 0, self.w), clamp(y, 0, self.h))
                    return

                if not held_keys['alt'] and not self.is_in_paste_mode:
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

                else:   # sample color
                    self.selected_char = self.grid[x][y]

        if mouse.right:     # selection
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
            self.rect_tool.position = self.rect_tool.start / Vec2(self.w, self.h)
            self.rect_tool.scale = (self.rect_tool.end - self.rect_tool.start) / Vec2(self.w, self.h)


    def get_cursor_position(self):
        y = int(round(self.cursor.y * self.h))
        x = int(round(self.cursor.x * self.w))
        return Vec2(x,y)


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

        if key == 'left mouse down' and self.canvas_collider.hovered and not self.is_in_paste_mode:
            self.start_pos = self.get_cursor_position()
            if not held_keys['control']:
                self.prev_draw = None

        if key == 'left mouse up' and self.start_pos:
            self.start_pos = None
            self.lock_axis = None
            self.render()

            if not held_keys['control']:
                self.record_undo()

        if key == 'right mouse down' and not self.is_in_paste_mode:
            if not held_keys['shift'] and not held_keys['alt']:
                self.selection_mode = 'overwrite'
                self.clear_selection()
            elif (held_keys['control'] or held_keys['shift']) and not held_keys['alt']:
                self.selection_mode = 'add'
            elif held_keys['alt'] and not (held_keys['control'] or held_keys['shift']):
                self.selection_mode = 'subtract'

            self.rect_selection[0] = self.get_cursor_position()


        if key == 'left mouse down' and self.is_in_paste_mode:
            self.exit_paste_mode()


        if key == 'right mouse down' and self.is_in_paste_mode:
            self.exit_paste_mode(discard=True)


        elif key == 'right mouse up':
            self.rect_tool.enabled = False
            # if self.selection_mode == 'overwrite':
            #     self.clear_selection()

            new_value = int(self.selection_mode == 'overwrite' or self.selection_mode == 'add')
            for y in range(self.rect_tool.start.Y, self.rect_tool.end.Y):
                for x in range(self.rect_tool.start.X, self.rect_tool.end.X):
                    self.selection_matrix[x][y] = new_value

            self.render_selection()


        if key == 'shift up':
            self._lock_origin = None

        if held_keys['control'] and key == 'z':
            self.undo_index -= 1
            self.undo_index = clamp(self.undo_index, 0, len(self.undo_stack)-1)
            self.grid = deepcopy(self.undo_stack[self.undo_index])
            self.render()

        if held_keys['control'] and key == 'y':
            self.undo_index += 1
            self.undo_index = clamp(self.undo_index, 0, len(self.undo_stack)-1)
            self.grid = deepcopy(self.undo_stack[self.undo_index])
            self.render()

        # fill
        if key == 'g' and self.canvas_collider.hovered:
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

        if held_keys['control'] and key == 'c':
            self.copy()

        if held_keys['control'] and key == 'v':
            self.enter_paste_mode()


    def record_undo(self):
        self.undo_index += 1
        self.undo_stack = self.undo_stack[:self.undo_index]
        self.undo_stack.append(deepcopy(self.grid))



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

        copy_data = [[tuple(self.grid[start_x+x][start_y+y]) for y in range(selection_height)] for x in range(selection_width)]
        pyperclip.copy(json.dumps(dict(data=copy_data)))


    def enter_paste_mode(self):
        self.is_in_paste_mode = True
        self.paste_data = json.loads(pyperclip.paste())
        if not self.paste_data['data']:
            return
        self.paste_data = self.paste_data['data']
        w = len(self.paste_data)
        h = len(self.paste_data[1])

        self.temp_paste_layer.enabled = True
        self.temp_paste_layer.scale = (w,h)

        if not self.temp_paste_layer.texture or self.temp_paste_layer.texture.size != (w,h):
            self.temp_paste_layer.texture = Texture(Image.new(mode='RGBA', size=(w,h), color=(0,0,0,0)))

        for x in range(w):
            for y in range(h):
                pixel = self.paste_data[x][y]
                if not pixel:
                    pixel = color.clear

                self.temp_paste_layer.texture.set_pixel(x, y, pixel)
        self.temp_paste_layer.texture.apply()


    def exit_paste_mode(self, discard=False):
        self.is_in_paste_mode = False
        self.temp_paste_layer.enabled = False
        x_offset = int(self.cursor.x * self.w)
        y_offset = int(self.cursor.y * self.h)
        w = len(self.paste_data)
        h = len(self.paste_data[1])

        if discard:
            return

        for x in range(w):
            for y in range(h):
                real_x = x + x_offset
                real_y = y + y_offset

                if real_x < 0 or real_x >= self.w or real_y < 0 or real_y >= self.h:
                    continue

                pixel = self.paste_data[x][y]
                if not pixel:
                    continue

                self.grid[x+x_offset][y+y_offset] = pixel

        self.clear_selection()
        self.render()


    def clear_selection(self):
        self.selection_matrix = [[0 for y in range(self.h)] for x in range(self.w)]
        self.selection_renderer.model.clear()
        print('clear selection')


    def render_selection(self):
        quad = load_model('quad', use_deepcopy=True)
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
        self.w, self.h = int(texture.size[0]), int(texture.size[1])
        self.canvas.scale_x = self.canvas.scale_y * self.w / self.h
        self.grid = [[texture.get_pixel(x,y) for y in range(texture.height)] for x in range(texture.width)]
        self.canvas.texture.filtering = None
        self.cursor.scale = Vec2(self.brush_size / self.w, self.brush_size / self.h)
        self.help_icon.scale = self.help_icon.target_scale
        self.selection_renderer.scale=(1/self.w,1/self.h)

        if clear_undo_stack:
            self.undo_stack.clear()
            self.undo_index = -1
        self.record_undo()

        if render:
            self.render()


    def draw(self, x, y):
        for _y in range(y, min(y+self.brush_size, self.h)):
            for _x in range(x, min(x+self.brush_size, self.w)):
                self.grid[_x][_y] = self.selected_char
                self.canvas.texture.set_pixel(_x, _y, self.grid[_x][_y])

        self.canvas.texture.apply()


    def render(self):
        for y in range(self.h):
            for x in range(self.w):
                self.canvas.texture.set_pixel(x, y, self.grid[x][y])

        self.canvas.texture.apply()


    def save(self):
        if self.canvas.texture.path:
            self.canvas.texture.save(self.canvas.texture.path)
            print('saved:', self.canvas.texture.path)

    @property
    def texture(self):
        if not hasattr(self, 'canvas'):
            return None
        return self.canvas.texture

    @texture.setter
    def texture(self, value):
        if hasattr(self, 'canvas'):
            self.canvas.texture = value



class ASCIIEditor(GridEditor):
    def __init__(self, size=(61,28), palette=(' ', '#', '|', 'A', '/', '\\', 'o', '_', '-', 'i', 'M', '.'), font='VeraMono.ttf', canvas_color=color.black, line_height=1.1, **kwargs):
        super().__init__(size=size, palette=palette, canvas_color=canvas_color, **kwargs)
        rotated_grid = list(zip(*self.grid[::-1]))
        text = '\n'.join([''.join(reversed(line)) for line in reversed(rotated_grid)])

        self.text_entity = Text(parent=self.parent, text=text, x=-.0, y=.5, line_height=line_height, font=font)

        self.scale = (self.text_entity.width, self.text_entity.height)
        self.canvas.scale = 1
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
        #     undo_stack = undo_stack[:undo_index]
        #     undo_stack.append(deepcopy(grid))




if __name__ == '__main__':
    app = Ursina(borderless=False)
    '''
    pixel editor example, it's basically a drawing tool.
    can be useful for level editors and such
    here we create a new texture, but can also give it an existing texture to modify.
    '''
    from PIL import Image
    t = Texture(Image.new(mode='RGBA', size=(32,32), color=(0,0,0,1)))
    from ursina.prefabs.grid_editor import PixelEditor
    editor = PixelEditor(parent=scene, texture=load_texture('brick'), scale=10)

    camera.orthographic = True
    camera.fov = 15
    EditorCamera(rotation_speed=0)
    # editor.selection_mover.enabled = True
    # editor.selection_mover.on_click()
    # editor.temp_layer.alpha = .5

    # '''
    # same as the pixel editor, but with text.
    # '''
    from ursina.prefabs.grid_editor import ASCIIEditor
    ASCIIEditor(x=0, scale=.1)

    app.run()
