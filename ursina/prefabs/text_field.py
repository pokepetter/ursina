from ursina import *
import pyperclip
# from tree_view import TreeView


class TextField(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera.ui,
            x=-.5,
            y=.4,
            ignore_paused=True,
            )


        self.font = 'VeraMono.ttf'
        self.line_height = 1
        # self.max_width = 80
        self.max_lines = 99999

        self.text_entity = Text(
            parent = self,
            start_tag='☾',
            end_tag = '☽',
            font = self.font,
            text='',
            line_height=self.line_height,
            origin=(-.5, .5),
            )
        self.line_numbers = Text(
            parent = self,
            font = self.font,
            text='0',
            origin=(.5,.5),
            x=-.04,
            color=color.gray,
            enabled = False,
            )
        self.character_width = Text.get_width('a', font=self.font)
        self.cursor_parent = Entity(parent=self, scale=(self.character_width, -1*Text.size))
        # self.max_line_indicatior = Entity(parent=self.cursor_parent, model='quad', origin=(-.5,.5), scale=(100,.05), rotation_x=180, color=color.red)
        # self.max_width_indicatior = Entity(
        #     parent=self.cursor_parent, model='quad', origin=(-.5,.5), scale=(100,.05), rotation_x=180, rotation_z=90, color=color.color(0,0,1,.05), x=80)
        self.cursor = Entity(parent=self.cursor_parent, model='cube', color=color.white33, origin=(-.5, -.5), scale=(.1, 1))
        self.bg = Entity(parent=self.cursor_parent, model='cube', color=color.dark_gray, origin=(-.5,-.5), z=1, scale=(120, 20), collider='box', visible=False)

        self.selection = None
        self.selection_parent = Entity(parent=self.cursor_parent)
        self.register_mouse_input = False

        def blink_cursor():
            if self.cursor.color == color.cyan:
                self.cursor.color = color.clear
            else:
                self.cursor.color = color.cyan
            invoke(blink_cursor, delay=.5)

        blink_cursor()
        self.text = ''

        self.replacements = dict()

        self.on_undo = list()
        self.on_redo = list()

        self.shifted_keys = {
            '-' : '_',
            '.' : ':',
            ',' : ';',
            '\'' : '*',
            '<' : '>',
            '+' : '?',
            '0' : '=',
            '1' : '!',
            '2' : '"',
            '3' : '#',
            # '4' : '¤',
            '5' : '%',
            '6' : '&',
            '7' : '/',
            '8' : '(',
            '9' : ')',
        }
        self.alted_keys = {
            '\'' : '´',
            '0' : '}',
            '2' : '@',
            '3' : '£',
            '4' : '¤',
            '5' : '€',
            '7' : '{',
            '8' : '[',
            '9' : ']',
        }
        self.shortcuts = {
            'newline':          ('enter', 'enter hold'),
            'erase':            ('backspace', 'backspace hold'),
            'erase_word':       ('ctrl+backspace', 'ctrl+backspace hold'),
            'delete_line':      ('ctrl+shift+k',),
            'undo':             ('ctrl+z', 'ctrl+z hold'),
            'redo':             ('ctrl+y', 'ctrl+y hold', 'ctrl+shift+z', 'ctrl+shift+z hold'),
            # 'save':             ('ctrl+s',),
            # 'save_as':          ('ctrl+shift+s',),
            'indent':           ('tab',),
            'dedent':           ('shift+tab',),
            'move_line_down':   ('ctrl+down arrow', 'ctrl+down arrow hold'),
            'move_line_up':     ('ctrl+up arrow', 'ctrl+up arrow hold'),
            # 'cut':              ('ctrl+x',),
            'copy':             ('ctrl+c',),
            'paste':            ('ctrl+v',),
            # 'select_all':       ('ctrl+a',),
            # 'toggle_comment':   ('ctrl+alt+c',),
            # 'find':             ('ctrl+f',),

            'move_left':        ('left arrow', 'left arrow hold'),
            'move_right':       ('right arrow', 'right arrow hold'),
            'move_up':          ('up arrow', 'up arrow hold'),
            'move_down':        ('down arrow', 'down arrow hold'),
            'move_to_end_of_word' : ('ctrl+right arrow', 'ctrl+right arrow hold'),
            'move_to_start_of_word' : ('ctrl+left arrow', 'ctrl+left arrow hold'),

            'select_word_left': ('ctrl+shift+left arrow', 'ctrl+shift+left arrow hold'),
            'select_word':      ('double click'),
        }

        # self.debug_cursor = Entity(parent=self.cursor_parent, model='cube', origin=(-.5,-.5), color=color.white33)


        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_text(self, s, move_cursor=True):
        x, y = int(self.cursor.x), int(self.cursor.y)

        lines = self.text.split('\n')
        l = lines[y]
        lines[y] =  l[:x] + s + l[x:]
        self.on_undo.append((self.text, y, x))
        self.text = '\n'.join(lines)

        if move_cursor:
            self.cursor.x += len(s)


    def move_line(self, a, b):
        x, y = int(self.cursor.x), int(self.cursor.y)

        lines = self.text.split('\n')
        lines[a], lines[b] = lines[b], lines[a]
        self.on_undo.append((self.text, y, x))
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

        self.on_undo.append((self.text, y, x))

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

    def delete_selected(self):
        lines = self.text.split('\n')
        self.cursor.position = self.selection[1]
        if int(self.selection[1][1]) > int(self.selection[0][1]):
            for y in range(int(self.selection[0][1]), int(self.selection[1][1])):
                lines.pop(y)
                print('delete line:', y)


        for x in range(int(self.selection[1][0]) - int(self.selection[0][0])):
            self.erase()
        # l = lines[int(self.selection[1])]

        self.text = '\n'.join(lines)
        self.selection = None
        # self.on_undo.append((self.text, y, x))
        self.draw_selection()


    def input(self, key):
        text, cursor, on_undo, add_text, erase = self.text, self.cursor, self.on_undo, self.add_text, self.erase

        if key == 'space':
            key = ' '
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

        delimiters = (' ', '.')
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
            # self.selection[0] = self.cursor.position
            print(self.selection)
            self.draw_selection()


        k = key.replace(' hold', '')
        k = k.replace('shift+', '')
        # print(Text.get_width('f'))
        if len(k) == 1 and not held_keys['control']:

            if held_keys['shift']:
                k = k.upper()
                if k in self.shifted_keys:
                    k = self.shifted_keys[k]
                if k in self.alted_keys:
                    k = self.alted_keys[k]

            if self.selection:  # delete selected text
                self.delete_selected()

            add_text(k)

            if k == '(':
                add_text(')')
                cursor.x -= 1

            if k == '[':
                add_text(']')
            if k == '{':
                add_text('}')


        if key in ('space', 'space hold'):
            add_text(' ')

        if key in self.shortcuts['newline'] and self.cursor.y < self.max_lines-1:
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
            if self.selection == None or self.selection[0] == self.selection[1]:
                add_text(' '*4, move_cursor=True)

            else:
                for y in range(self.selection[0][1], self.selection[1][1]+1):
                    # print('indent', y)
                    lines[y] = (' '*4) + lines[y]

                self.cursor.x += 4
                self.on_undo.append((self.text, y, x))
                self.text = '\n'.join(lines)


        if key in self.shortcuts['dedent']:
            if self.selection == None:
                if l.startswith(' '*4):
                    lines[y] = l[4:]
            else:
                for y in range(self.selection[0][1], self.selection[1][1]+1):
                    l = lines[y]
                    if l.startswith(' '*4):
                        # print('dedent')
                        lines[y] = l[4:]

            self.cursor.x -= 4
            self.cursor.x = max(self.cursor.x, 0)
            self.on_undo.append((self.text, y, x))
            self.text = '\n'.join(lines)


        if key in self.shortcuts['erase']:
            if not self.selection:
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
            self.on_undo.append((self.text, y, x))
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

            # self.on_redo.append((self.text, y, x))
            self.text = on_undo[-1][0]
            cursor.y = on_undo[-1][1]
            cursor.x = on_undo[-1][2]
            on_undo.pop()

        # if key in self.shortcuts['redo']:
        #     if not self.on_redo:
        #         return
        #     self.text = self.on_redo[-1][0]
        #     cursor.y = self.on_redo[-1][1]
        #     cursor.x = self.on_redo[-1][2]
        #     self.on_redo.pop()


        if key in self.shortcuts['delete_line']:
            lines.pop(y)

            if y == 0:
                self.cursor.x = 0
            else:
                self.cursor.x = len(lines[y-1])

            if y >= len(lines) and y > 0:
                self.cursor.y -= 1

            self.text = '\n'.join(lines)


        if key == self.shortcuts['select_word']:
            pass
            # move cursor to the begining
            # select word right

        if key in self.shortcuts['copy']:
            print('-----copy:', self.selection)

        if key in self.shortcuts['paste']:
            self.add_text(pyperclip.paste())


        if self.register_mouse_input:
            if key == 'left mouse down' and mouse.hovered_entity == self.bg:
                # if mouse.x < self.x:
                #     return
                # from math import floor
                x = round(mouse.point[0] * self.bg.scale_x)
                y = floor(mouse.point[1] * self.bg.scale_y)

                cursor.position = (x, y)
                click_position = cursor.position
                self.selection = [click_position, click_position]


            if key == 'left mouse up':
                # if mouse.x < self.x:
                #     return

                x = round(mouse.point[0] * self.bg.scale_x)
                y = floor(mouse.point[1] * self.bg.scale_y)

                cursor.position = (x, y)
                click_position = cursor.position
                self.selection[1] = click_position

                if self.selection[1][1] < self.selection[0][1]:
                    self.selection = [self.selection[1], self.selection[0]]

                self.draw_selection()

        self.render()


    def render(self):
        lines = self.text.split('\n')
        text = '\n'.join(lines[0:self.max_lines+1])

        if self.replacements:
            self.text_entity.text = multireplace(text, self.replacements)
        else:
            self.text_entity.text = text
        self.line_numbers.text = '\n'.join([str(e) for e in range(min(len(lines), self.max_lines))])
        self.line_numbers.color = color.gray



    def update(self):
        # self.debug_cursor.position = self.get_mouse_position()

        if self.register_mouse_input and mouse.left:
            x = round(mouse.point[0] * self.bg.scale_x)
            y = floor(mouse.point[1] * self.bg.scale_y)

            self.cursor.position = (x, y)
            click_position = self.cursor.position
            self.selection[1] = click_position

            # if self.selection[1][1] < self.selection[0][1]:
            #     self.selection = [self.selection[1], self.selection[0]]

            self.draw_selection()


    def select_all(self):
        lines = self.text.split('\n')
        lines = self.text.splitlines()
        # print('|||||||||', len(lines), len(self.text.splitlines()), self.text.splitlines(), lines)
        if lines:
            self.selection = [(0,0), (len(lines[-1]), len(lines))]
            print(self.selection)


    def draw_selection(self):
        [destroy(c) for c in self.selection_parent.children]

        if self.selection == None:
            return


        if self.selection[0] == self.selection[1]:
            return

        start_y = int(self.selection[0][1])
        end_y = int(self.selection[1][1])
        lines = self.text.split('\n')

        # draw selection
        for y in range(int(self.selection[0][1]), int(self.selection[1][1])):
            e = Entity(parent=self.selection_parent, model='cube', origin=(-.5, -.5),
                color=color.color(120,1,1,.1), double_sided=True, position=(0,y*1.15), ignore=True, scale_x=len(lines[y]))
            if y == self.selection[0][1]:
                e.x = self.selection[0][0]
                e.scale_x -= self.selection[0][0]

        e = Entity(parent=self.selection_parent, model='cube', origin=(-.5, -.5),
            color=color.color(120,1,1,.1), double_sided=True, position=(0,end_y*1.15),
            ignore=True, scale_x=self.selection[1][0])
        if self.selection[0][1] == self.selection[1][1]:
            e.x = self.selection[0][0]
            e.scale_x -= self.selection[0][0]


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
    te = TextField(max_lines=300, scale=1)
    # te.line_numbers.enabled = True
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
    te.text = dedent('''
        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Aliquam sapien tellus, venenatis sit amet ante et, malesuada porta risus.
        Etiam et mi luctus, viverra urna at, maximus eros. Sed dictum faucibus purus,
        nec rutrum ipsum condimentum in. Mauris iaculis arcu nec justo rutrum euismod.
        Suspendisse dolor tortor, congue id erat sit amet, sollicitudin facilisis velit.'''
        )[1:]
    # te.cursor.position = (4,0)
    # te.selection = [(25,0), (10,3)]
    # te.draw_selection()
    te.render()
    # te.selection = ((0,0),(4,0))
    # te.select_all()
    # te.selection = ((1,0),(3,0))
    # te.selection = ((2,3),(0,0))
    # te.draw_selection()

    app.run()
