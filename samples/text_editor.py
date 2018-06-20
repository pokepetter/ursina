from ursina import *


class TextEditor(Entity):

    def __init__(self):

        super().__init__()
        self.text = Text('--------')
        self.text.font = 'Inconsolata-Regular.ttf'
        self.text.line_height = 1.1
        # self.text.parent = scene.ui
        # self.text.position = (-.4 * 1.7, .4)
        # self.text.position = (0, 0)
        self.bg = Quad(color=color.black33, origin=(-.5, .5))

        # self.o = Quad(scale = (.1, .1))
        # self.bg.scale = self.text.getTightBounds()

        # self.text.align = 'top_left'
        self.text.scale *= 4
        self.character_width = .5
        self.real_text = '''class TextEditor(Entity):

    def __init__(self):

        super().__init__()
        self.text = Text()
        self.text.parent = scene.ui
        # self.text.position = (-.4 * 1.7, .4)
        'strings should be green'
        .text = Text()
        '''

        self.replacements = {
            'class '    : '<violet>class <default>',
            ' def '     : '<violet> def <default>',
            'self'      : '<orange>self<default>',
            '__init__'  : '<cyan>__init__<default>',
            'Entity'    : '<lime>Entity<default>',
            # '\''        : '<green>\'',
            # '\' '       : '\' <default>',    #end quote space
            # '\'\n'      : '\'<default>\n'    #end quote newline
            }

        self.indicator = Entity(
            model = 'circle_16',
            origin = (0, .5),
            y = -.2,
            color = color.azure,
            z = -.1,
            scale = (.15, .15)
            
        self.indicator_line = Entity(
            parent = self.indicator,
            model = 'quad',
            color = color.azure,
            origin = (0, -.5, -.1),
            scale = (.5, 1 / self.indicator.scale_y)
            )

    def move_indicator(self, x, y):
        self.indicator.x += self.character_width * x
        self.indicator.y += self.text.line_height * y
        self.indicator.x = clamp(self.indicator.x, 0, 60)
        self.indicator.y = clamp(self.indicator.y, -1000, 0)

    # def move_indicator_to(self, x, y):
    #     self.indicator.x = self.character_width * x
    #     self.indicator.y = self.text.line_height * y
    #     self.indicator.x = clamp(self.indicator.x, 0, 60)
    #     self.indicator.y = clamp(self.indicator.y, -1000, 0)

# self.indicator.
    def input(self, key):
        if key == 'scroll up':
            camera.y += 1
        if key == 'scroll down':
            camera.y -= 1

        if held_keys['left shift']:
            if key == 'd' or key == 'd hold':
                self.move_indicator(1, 0)
            if key == 'a' or key == 'a hold':
                self.move_indicator(-1, 0)
            if key == 'w' or key == 'w hold':
                self.move_indicator(0, 1)
            if key == 's' or key == 's hold':
                self.move_indicator(0, -1)
            if key == 'e' or key == 'e hold':
                self.indicator.x += 10 # to end of word
            if key == 'q' or key == 'q hold':
                self.indicator.x -= 10

        elif key == 'arrow right' or key == 'arrow right hold':
            self.move_indicator(1, 0)
        elif key == 'arrow left' or key == 'arrow left hold':
            self.move_indicator(-1, 0)
        elif key == 'arrow up' or key == 'arrow up hold':
            self.move_indicator(0, 1)
        elif key == 'arrow down' or key == 'arrow down hold':
            self.move_indicator(0, -1)



        else:
            # print('insert at line:', - int(self.indicator.y / self.text.line_height),
            #     'pos:',
            #     )

            x = int(self.indicator.x / self.character_width)
            y = -int(self.indicator.y / self.text.line_height)
            lines = self.real_text.splitlines()

            if len(key) == 1:
                lines[y] = lines[y][0:x] + key + lines[y][x:]
                self.move_indicator(1, 0)

            elif key == 'backspace' or key == 'backspace hold':
                if x > 0:
                    lines[y] = lines[y][0:x-1] + lines[y][x:]
                    self.move_indicator(-1, 0)

            elif key == 'enter' or key == 'enter hold':
                # find indent
                indent = ''
                for c in lines[y]:
                    if c.isspace():
                        indent += ' '
                    else:
                        break
                lines[y] = lines[y][0:x] + '\n' + indent + lines[y][x:]
                self.indicator.x = 0
                self.move_indicator(len(indent), -1)

            elif key == 'space' or key == 'space hold':
                lines[y] = lines[y][0:x] + ' ' + lines[y][x:]
                self.move_indicator(1, 0)


            self.real_text = '\n'.join(lines)



            # self.text.text = self.real_text.replace('def', '<violet>def <default>')
            self.text.text = multireplace(self.real_text, self.replacements)

        if key == 'left mouse down':
            print(mouse.x, mouse.y, camera.y)

    # def find_nth(self, string, substring, index):
    #     return string.find(substring, string.find(substring) + index + 1)

    # def find_nth(self, s, x, n):
    #     i = -1
    #     for _ in range(n):
    #         i = s.find(x, i + len(x))
    #         if i == -1:
    #             break
    #     return i



if __name__ == '__main__':
    loadPrcFileData('', 'win-size 256 512')
    app = main.Ursina()
    # window.size = (256, 512)
    camera.orthographic = True
    camera.fov = 60
    camera.x = camera.fov * .4
    camera.y = -camera.fov * .25
    window.color = color.color(0, 0, .1)
    # window.fps_counter = False
    s = TextEditor()
    app.run()
