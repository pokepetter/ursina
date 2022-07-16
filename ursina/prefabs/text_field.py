from ursina import *
import pyperclip
# from tree_view import TreeView


class TextField(Entity):
    def __init__(self, max_lines=9999, **kwargs):
        super().__init__(parent=camera.ui, x=-.5, y=.4, ignore_paused=True)

        self.font = 'VeraMono.ttf'
        self.line_height = 1
        self.max_lines = max_lines
        self.character_limit = None

        self.scroll_parent = Entity(parent=self)
        self.text_entity = Text(parent=self.scroll_parent, start_tag='☾', end_tag='☽', font=self.font, text='', line_height=self.line_height, origin=(-.5, .5))
        self.line_numbers = Text(parent=self.scroll_parent, font=self.font, text='0', origin=(.5,.5), x=-.04, color=color.gray, enabled=False)
        self.character_width = Text.get_width('a', font=self.font)
        self.cursor_parent = Entity(parent=self.scroll_parent, scale=(self.character_width, -1*Text.size))
        self.cursor = Entity(name='text_field_cursor', parent=self.cursor_parent, model='cube', color=color.cyan, origin=(-.5, -.5), scale=(.1, 1, 0), enabled=False)
        self.cursor.blink(duration=1.2, loop=True)
        # self.max_line_indicatior = Entity(parent=self.cursor_parent, model='quad', origin=(-.5,.5), scale=(100,.05), rotation_x=180, color=color.red)
        # self.max_width_indicatior = Entity(
        #     parent=self.cursor_parent, model='quad', origin=(-.5,.5), scale=(100,.05), rotation_x=180, rotation_z=90, color=color.color(0,0,1,.05), x=80)

        self.bg = Entity(name='text_field_bg', parent=self, model='cube', color=color.dark_gray, origin=(-.5,.5), z=0.005, scale=(120, Text.size*self.max_lines, 0.001), collider='box', visible=True)

        self.selection = [Vec2(0,0), Vec2(0,0)]
        self.selection_parent = Entity(name='text_field_selection_parent', parent=self.cursor_parent, scale=(1,1,0))
        self.register_mouse_input = False
        self.world_space_mouse = False

        self.triple_click_delay = 0.3
        self._last_double_click = 0
        self.scroll = 0
        self._prev_scroll = self.scroll

        self.active = True
        self.highlight_color = color.color(120,1,1,.1)
        self.text = ''
        self.replacements = dict()
        self.on_undo = []
        self.on_redo = []
        self.on_value_changed = None

        self.shortcuts = {
            'newline':          ('enter', 'enter hold'),
            'erase':            ('backspace', 'backspace hold'),
            'erase_word':       ('ctrl+backspace', 'ctrl+backspace hold'),
            'delete_line':      ('ctrl+shift+k',),
            'duplicate_line':   ('ctrl+d',),
            'undo':             ('ctrl+z', 'ctrl+z hold'),
            'redo':             ('ctrl+y', 'ctrl+y hold', 'ctrl+shift+z', 'ctrl+shift+z hold'),
            # 'save':             ('ctrl+s',),
            # 'save_as':          ('ctrl+shift+s',),
            'indent':           ('tab',),
            'dedent':           ('shift+tab',),
            'move_line_down':   ('ctrl+down arrow', 'ctrl+down arrow hold'),
            'move_line_up':     ('ctrl+up arrow', 'ctrl+up arrow hold'),
            'scroll_up':        ('scroll up',),
            'scroll_down':      ('scroll down',),
            'cut':              ('ctrl+x',),
            'copy':             ('ctrl+c',),
            'paste':            ('ctrl+v',),
            'select_all':       ('ctrl+a',),
            # 'toggle_comment':   ('ctrl+alt+c',),
            # 'find':             ('ctrl+f',),

            'move_left':        ('left arrow', 'left arrow hold'),
            'move_right':       ('right arrow', 'right arrow hold'),
            'move_up':          ('up arrow', 'up arrow hold'),
            'move_down':        ('down arrow', 'down arrow hold'),
            'move_to_end_of_word' : ('ctrl+right arrow', 'ctrl+right arrow hold'),
            'move_to_start_of_word' : ('ctrl+left arrow', 'ctrl+left arrow hold'),

            'select_word_left': ('ctrl+shift+left arrow', 'ctrl+shift+left arrow hold'),
            'select_word':      ('double click',),
            'select_line':      ('triple click',),
        }


        for key, value in kwargs.items():
            setattr(self, key, value)

        self._prev_text = ''


    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self.cursor.enabled = value

        if not value:
            self.selection = None
            self.draw_selection()


    def add_text(self, s, move_cursor=True):
        if self.character_limit and len(self.text) >= self.character_limit:
            return

        x, y = int(self.cursor.x), int(self.cursor.y)

        lines = self.text.split('\n')
        l = lines[y]
        lines[y] =  l[:x] + s + l[x:]
        self._append_undo(self.text, y, x)
        self.text = '\n'.join(lines)

        if move_cursor:
            self.cursor.x += len(s)

    def _append_undo(self, text, y, x, clear_redo = True):
        if clear_redo:
            self.on_redo.clear()
        self.on_undo.append((text, y, x))


    def move_line(self, a, b):
        x, y = int(self.cursor.x), int(self.cursor.y)

        lines = self.text.split('\n')
        lines[a], lines[b] = lines[b], lines[a]
        self._append_undo(self.text, y, x)
        self.text = '\n'.join(lines)
        # print('moved line')


    def erase(self):
        # if not self.selection or self.selection[0] == self.selection[1]:
        x, y = int(self.cursor.x), int(self.cursor.y)
        if x+y == 0:
            return

        lines = self.text.split('\n')
        l = lines[y]
        # delete \n and go to line above
        if x == 0 and y > 0:
            new_x = len(lines[y-1])
            lines[y-1] += l
            lines.pop(y)
            self.cursor.x = new_x
            self.cursor.y -= 1
        # delete tab
        elif l[:x].lstrip() == '' and x >=4:
            l = l[4:]
            self.cursor.x -= 4
            lines[y] = l
        # normal erase
        else:
            removed = l[x-1]

            l = l[:x-1] + l[x:]
            self.cursor.x -= 1

            lines[y] = l

        self._append_undo(self.text, y, x)

        # else:   # delete selected
        #     self.delete_selected()
        #     lines = self.text.split('\n')
        #
        #     start_y = int(self.selection[0][1])
        #     end_y = int(self.selection[1][1])
        #
        #     if start_y == end_y:    # one line
        #         l = lines[start_y]
        #         start_x, end_x = int(self.selection[0][0]), int(self.selection[1][0])
        #         l = l[:start_x] + l[end_x:]
        #         lines[start_y] = l
        #         self.selection = (self.selection[0], self.selection[0])
        #         self.cursor.position = self.selection[0][0]
                # self.selection = None
                # self.selection[0][0],start_y),
                # ignore=True, scale_x=self.selection[1][0]-self.selection[0][0])
            # for y in range(int(self.selection[0][1]), int(self.selection[1][1])):
            #     lines.pop(y)




        self.text = '\n'.join(lines)

    def _ordered_selection(self):
        if not self.selection:
            return None
        if self.selection[1][1] < self.selection[0][1] or (self.selection[1][1] == self.selection[0][1] and self.selection[1][0] < self.selection[0][0]):
            return [self.selection[1], self.selection[0]]
        return self.selection


    def delete_selected(self):
        if not self.selection or self.selection[0] == self.selection[1]:
            return

        sel = self._ordered_selection()
        self.cursor.position = sel[0]
        start_y = int(sel[0][1])
        end_y = int(sel[1][1])
        lines = self.text.split('\n')

        lines[start_y] = lines[start_y][:int(sel[0][0])] + lines[end_y][int(sel[1][0]):]
        del lines[(start_y + 1) : (end_y + 1)]

        self._append_undo(self.text, self.cursor.y, self.cursor.x)
        self.text = '\n'.join(lines)
        self.selection = None
        # self._append_undo(self.text, y, x)
        self.draw_selection()


    def get_selected(self):
        if not self.selection or self.selection[0] == self.selection[1]:
            return None

        sel = self._ordered_selection()
        start_y = int(sel[0][1])
        end_y = int(sel[1][1])
        lines = self.text.split('\n')

        selected_text = ''
        # selected_text = lines[start_y][]

        for y in range(start_y, end_y+1):
            if y > start_y:
                selected_text += '\n'
            selected_text += lines[y][(int(sel[0][0]) if y == start_y else 0) : (int(sel[1][0]) if y == end_y else len(lines[y])) ]

        return selectedText


    def get_mouse_position_unclamped(self):
        if self.world_space_mouse:
            if mouse.point:
                x = round(mouse.point[0] * self.bg.scale_x)
                y = floor(mouse.point[1] * self.bg.scale_y)
            else:
                x = int(self.cursor.x)
                y = int(self.cursor.y)

        else:
            mpos = mouse.position
            mpos.x = mpos.x / self.world_scale_x * camera.ui.world_scale_x
            mpos.y = mpos.y / self.world_scale_y * camera.ui.world_scale_y
            mpos += camera.ui.get_position(self.text_entity)

            x = round(mpos.x / self.cursor_parent.scale_x)
            y = floor(mpos.y / self.cursor_parent.scale_y)

        return (x, y)


    def get_mouse_position(self):
        (x, y) = self.get_mouse_position_unclamped()

        lines = self.text.split('\n')
        y = clamp(y, 0, len(lines) - 1)
        x = clamp(x, 0, len(lines[y]))

        return (x, y)


    def input(self, key):
        # print('---', key)
        text, cursor, on_undo, add_text, erase = self.text, self.cursor, self.on_undo, self.add_text, self.erase

        if mouse.hovered_entity == self.bg:
            if key in self.shortcuts['scroll_down']:
                self.scroll = clamp(self.scroll+1, 0, self.max_lines)
                self.render()

            elif key in self.shortcuts['scroll_up']:
                self.scroll = clamp(self.scroll-1, 0, self.max_lines)
                self.render()


        if self.register_mouse_input and key == 'left mouse down':
            self.active = (mouse.hovered_entity == self.bg)

        if not self.active:
            return

        if key == 'double click':
            t = time.time()
            if t - self._last_double_click < self.triple_click_delay:
                key = 'triple click'
            self._last_double_click = t

        # key = f'{"ctrl" if held_keys["control"]} + {key}'
        ctrl, shift, alt = '', '', ''
        if held_keys['control'] and key != 'control':
            ctrl = 'ctrl+'
        if held_keys['shift'] and key != 'shift':
            shift = 'shift+'
        if held_keys['alt'] and key != 'alt':
            alt = 'alt+'

        key = ctrl+shift+alt+key
        # print(key)
        x, y = int(cursor.x), int(cursor.y)
        lines = text.split('\n')
        l = lines[y]

        if key in self.shortcuts['move_up']:
            if y > 0:
                cursor.y -= 1
                cursor.x = min(x, len(lines[y-1]))
        if key in self.shortcuts['move_down']:
            if y < len(lines)-1:
                cursor.y += 1
                cursor.x = min(x, len(lines[y+1]))
        if key in self.shortcuts['move_right']:
            if x == len(l) and y < len(lines)-1:        # end of line, move to beginning of next
                cursor.y += 1
                cursor.x = 0
            elif x < len(l):
                cursor.x += 1
        if key in self.shortcuts['move_left']:
            if x > 0:
                cursor.x -= 1
            elif y > 0:                                 # move to end of line above
                cursor.y -= 1
                cursor.x = len(lines[y-1])

        delimiters = ' .,!?;:(){}[]<>\'\"@#$%^&*+=-\\|/`~'
        if key in self.shortcuts['move_to_end_of_word']:
            if x == len(l):
                if y < len(lines)-1:        # end of line, move to beginning of next
                    cursor.y += 1
                    cursor.x = 0
                return

            elif l[x] not in delimiters:                # move right to closest delimiter
                for x in range(x, len(l)):
                    if l[x] in delimiters:
                        cursor.x = x
                        return
                cursor.x = len(l)
            else:                                       # move right to closest word
                for x in range(x, len(l)):
                    if l[x] not in delimiters:
                        cursor.x = x
                        return
                cursor.x = len(l)

        if key in self.shortcuts['move_to_start_of_word']:
            if x == 0 and y == 0:
                pass

            elif x == 0 and y > 0:                        # move to end of line above
                cursor.y -= 1
                cursor.x = len(lines[y-1])

            elif l[x-1] not in delimiters:              # move left to closest delimiter
                for x in range(x-1, 0, -1):
                    if l[x] in delimiters:
                        cursor.x = x+1
                        return
                cursor.x = 0
            else:                                       # move left to closest word
                for x in range(x-1, 0, -1):
                    if l[x] not in delimiters:
                        cursor.x = x+1
                        return
                cursor.x = 0

        if key in self.shortcuts['select_word_left']:
            self.selection[1] = self.cursor.position
            self.input(self.shortcuts['move_to_start_of_word'][0])
            self.selection[0] = self.cursor.position
            # print(self.selection)
            self.draw_selection()

        if key in self.shortcuts['newline'] and self.cursor.y < self.max_lines-1:
            if self.selection:
                self.delete_selected()

            if l.startswith('class ') and not l.endswith(':'):
                add_text(':')
            if l.startswith('def ') and not l.endswith(':'):
                add_text(':')

            add_text('\n')

            if l.strip() == '':
                indent = len(l)
            else:
                indent = len(l) - len(l.lstrip())
                if l.lstrip().startswith('class ') or l.lstrip().startswith('def '):
                    indent += 4

            self.cursor.y += 1
            self.cursor.x = 0
            add_text(' '*indent)
            # self.cursor.x = indent

        if key in self.shortcuts['indent']:
            if not self.selection or self.selection[0] == self.selection[1]:
                add_text(' '*4, move_cursor=True)

            else:
                for y in range(int(self.selection[0][1]), int(self.selection[1][1])+1):
                    # print('indent', y)
                    lines[y] = (' '*4) + lines[y]
                self.cursor.x += 4
                self._append_undo(self.text, y, x)
                self.text = '\n'.join(lines)


        if key in self.shortcuts['dedent']:
            if not self.selection or self.selection[0] == self.selection[1]:
                if l.startswith(' '*4):
                    lines[y] = l[4:]
            else:
                for y in range(int(self.selection[0][1]), int(self.selection[1][1])+1):
                    l = lines[y]
                    if l.startswith(' '*4):
                        # print('dedent')
                        lines[y] = l[4:]
                        if y == int(cursor.y):
                            moveCursor = True

            self.cursor.x = max(self.cursor.x - 4, 0)
            self._append_undo(self.text, y, x)
            self.text = '\n'.join(lines)


        if key in self.shortcuts['erase']:
            if not self.selection or self.selection[1] == self.selection[0]:
                erase()
            else:
                self.delete_selected()

        if key in self.shortcuts['erase_word']:
            # print('delete word')
            if x == 0:
                erase()
                return

            if not ' ' in l:
                l = l[x:]
                self.cursor.x = 0

            else:
                removed = ''
                beginning = l[:x]


                if beginning.endswith('  '): # delete whitespace
                    beginning = beginning.rstrip()
                    removed = ' ' * (x-len(beginning))

                for delimiter in ('.', '\'', '\"', '(', '"', '\''):
                    beginning = beginning.replace(delimiter, ' ')

                if not ' ' in beginning: # first word of the line
                    beginning = ''
                else:
                    beginning = beginning.rstrip().rsplit(' ', 1)[0]

                removed = l[len(beginning):x]

                l = beginning + l[x:]
                self.cursor.x -= len(removed)


            lines[y] = l
            self._append_undo(self.text, y, x)
            self.text = '\n'.join(lines)


        if key in self.shortcuts['move_line_down'] and self.cursor.y < self.max_lines:
            # print('move down')
            if y+1 == len(lines): # if at last line
                self.text += '\n'

            self.move_line(y, y+1)
            cursor.y += 1

        if key in self.shortcuts['move_line_up'] and y > 0:
            self.move_line(y, y-1)
            cursor.y -= 1


        if key in self.shortcuts['undo']:
            if not on_undo:
                return

            self.on_redo.append((self.text, y, x))
            self.text = on_undo[-1][0]
            cursor.y = on_undo[-1][1]
            cursor.x = on_undo[-1][2]
            on_undo.pop()

        if key in self.shortcuts['redo']:
            if not self.on_redo:
                return

            on_undo.append((self.text, y, x))
            self.text = self.on_redo[-1][0]
            cursor.y = self.on_redo[-1][1]
            cursor.x = self.on_redo[-1][2]
            self.on_redo.pop()


        if key in self.shortcuts['delete_line']:
            self._append_undo(self.text, y, 0)
            lines.pop(y)

            if y == 0:
                self.cursor.x = 0
            else:
                self.cursor.x = len(lines[y-1])

            if y >= len(lines) and y > 0:
                self.cursor.y -= 1

            self.text = '\n'.join(lines)

        if key in self.shortcuts['duplicate_line']:
            if len(lines) < self.max_lines:
                self._append_undo(self.text, y, 0)
                lines.insert(y, lines[y])
                self.text = '\n'.join(lines)


        if key in self.shortcuts['select_word']:
            for start_x in range(x, -1, -1):
                if l[start_x] in delimiters:
                    break
            if start_x > 0:
                start_x += 1

            for end_x in range(x, len(l)):
                if l[end_x] in delimiters:
                    break
            if end_x == len(l)-1:
                end_x += 1


            self.selection = [Vec2(start_x, y), Vec2(end_x, y)]
            self.draw_selection()
            return

        if key in self.shortcuts['select_line']:
            self.selection = [Vec2(0, y), Vec2(len(lines[y]), y)]
            self.cursor.position = self.selection[1]
            self.draw_selection()
            return

        if key in self.shortcuts['copy']:# TODO
            selectedText = self.get_selected()
            if selectedText:
                pyperclip.copy(selectedText)
                # print('-----copy:', selectedText)

        if key in self.shortcuts['paste']:# TODO
            if self.selection:
                self.delete_selected()
            self.add_text(pyperclip.paste())

        if key in self.shortcuts['cut']:# TODO
            selectedText = self.get_selected()
            if selectedText:
                pyperclip.copy(selectedText)
                self.delete_selected()
                # print('-----cut:', selectedText)

        if key in self.shortcuts['select_all']:
            self.select_all()


        elif self.register_mouse_input:
            if key == 'left mouse down' and mouse.hovered_entity == self.bg and mouse.point is not None:
                cursor.position = self.get_mouse_position()
                self.selection = [self.cursor.position, self.cursor.position]
                self.draw_selection()

            if key == 'left mouse up':
                    cursor.position = self.get_mouse_position()

                    if self.selection:
                        self.selection[1] = self.cursor.position


        self.render()


    def keystroke(self, key):
        cursor, add_text = self.cursor, self.add_text

        if not self.active:
            return

        if self.selection:  # delete selected text
            self.delete_selected()

        add_text(key)

        if key == '(':
            add_text(')')
            cursor.x -= 1
        elif key == '[':
            add_text(']')
            cursor.x -= 1
        elif key == '{':
            add_text('}')
            cursor.x -= 1

        self.render()


    def render(self):
        lines = self.text.split('\n')

        text = '\n'*self.scroll + '\n'.join(lines[self.scroll : self.max_lines + self.scroll])

        if not hasattr(self.text_entity, 'raw_text') or self._prev_text != text or self.scroll != self._prev_scroll:
            # print(self.scroll)

            if self.replacements:
                self.text_entity.text = multireplace(text, self.replacements)
            else:
                self.text_entity.text = text

            self.line_numbers.text = ('     \n'*self.scroll) + '\n'.join([str(e + self.scroll).rjust(5, '-') for e in range(min(len(lines), self.max_lines))])

            self._prev_text = text
            self._prev_scroll = self.scroll
            self.scroll_parent.y = (self.scroll * Text.size)
            # self.cursor.y
            self.draw_selection()

        if self.on_value_changed:
            self.on_value_changed()



    def update(self):
        if self.register_mouse_input and mouse.left and mouse.moving:
            self.cursor.position = self.get_mouse_position()
            if self.selection:
                self.selection[1] = self.cursor.position

            self.draw_selection()


    def select_all(self):
        lines = self.text.split('\n')
        lines = self.text.splitlines()
        # print('|||||||||', len(lines), len(self.text.splitlines()), self.text.splitlines(), lines)
        if lines:
            self.selection = [(0,0), (len(lines[-1]), len(lines) - 1)]
            print(self.selection)

        self.draw_selection()


    def draw_selection(self):
        [destroy(c) for c in self.selection_parent.children]

        if not self.selection or self.selection[0] == self.selection[1]:
            return

        sel = self._ordered_selection()
        # print('---', self.selection, self.scroll)

        start_y = int(sel[0].y)
        end_y = int(sel[1].y)
        lines = self.text.split('\n')
        if start_y == end_y:
            e = Entity(parent=self.selection_parent, model='cube', origin=(-.5,-.5), color=self.highlight_color, ignore=True, y=start_y)
            e.x = sel[0].x
            e.scale_x = sel[1].x - sel[0].x
            return

        # first line
        if start_y >= self.scroll and start_y < self.scroll+self.max_lines:
            e = Entity(parent=self.selection_parent, model='quad', origin=(-.5, -.5),
            color=self.highlight_color, double_sided=True, position=(sel[0].x,start_y), ignore=True)
            e.scale_x = len(lines[start_y]) - sel[0].x

        # middle lines
        for y in range(max(start_y+1, self.scroll), min(end_y, self.scroll+self.max_lines)):
            e = Entity(parent=self.selection_parent, model='quad', origin=(-.5, -.5),
                color=self.highlight_color, double_sided=True, position=(0,y), ignore=True, scale_x=len(lines[y]))

        # last line
        if end_y >= self.scroll and end_y < self.scroll+self.max_lines:
            e = Entity(parent=self.selection_parent, model='quad', origin=(-.5, -.5),
            color=self.highlight_color, double_sided=True, position=(0,end_y), ignore=True)
            e.scale_x = sel[1].x



if __name__ == '__main__':
    app = Ursina()
    # camera.orthographic = True
    # camera.fov = 1
    # window.size = window.fullscreen_size
    window.x = 200

    window.color = color.color(0, 0, .1)
    Button.color = color._20
    window.color = color._25

    # Text.size = 1/window.fullscreen_size[1]*16
    Text.default_font = 'consola.ttf'
    Text.default_resolution = 16*2
    # TreeView()
    te = TextField(max_lines=20, scale=1, register_mouse_input = True)
    #te = TextField(max_lines=300, scale=1, register_mouse_input = True, scroll_size = (50,3))
    te.line_numbers.enabled = True
    # for name in color.color_names:
    #     if name == 'black':
    #         continue
    #     te.replacements[f' {name}'] = f'☾{name}☽ {name}☾default☽'
    # te.replacements = {
    #     'class ':    '☾orange☽class ☾default☽',
    #     'def ':      '☾azure☽def ☾default☽',
    #     '__init__':  '☾cyan☽__init__☾default☽',
    #     'Entity':    '☾lime☽Entity☾default☽',
    #     'self.':     '☾orange☽self☾default☽.',
    #     '(self)':     '(☾orange☽self☾default☽)',
    #     'self,':     '☾orange☽self☾default☽,',
    #     '    ':      '☾dark_gray☽----☾default☽',
    #     }
    #
    import textwrap
    te.text = "\n".join(textwrap.wrap(dedent('''
        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Aliquam sapien tellus, venenatis sit amet ante et, malesuada porta risus.
        Etiam et mi luctus, viverra urna at, maximus eros. Sed dictum faucibus purus,
        nec rutrum ipsum condimentum in. Mauris iaculis arcu nec justo rutrum euismod.
        Suspendisse dolor tortor, congue id erat sit amet, sollicitudin facilisis velit.'''
        ), 10))[1:]
    te.render()

    app.run()
