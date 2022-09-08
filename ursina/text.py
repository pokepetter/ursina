from panda3d.core import TransparencyAttrib
from panda3d.core import Filename
from panda3d.core import TextNode
# from direct.interval.IntervalGlobal import Sequence, Func, Wait, SoundInterval

import ursina
# from ursina import *
from ursina import camera
from ursina.entity import Entity
from ursina.sequence import Sequence, Func, Wait
from ursina import color
# note:
# <scale:n> tag doesn't work well in the middle of text.
# only good for titles for now.

class Text(Entity):

    size = .025
    default_font = 'OpenSans-Regular.ttf'
    default_resolution = 1080 * size * 2
    start_tag = '<'
    end_tag = '>'

    def __init__(self, text='', start_tag=start_tag, end_tag=end_tag, ignore=True, **kwargs):
        super().__init__(ignore=ignore)
        self.size = Text.size
        self.parent = camera.ui

        self.setColorScaleOff()
        self.shader = None
        self.text_nodes = []
        self.images = []
        self.origin = (-.5, .5)

        self.font = Text.default_font
        self.resolution = Text.default_resolution
        self.line_height = 1
        self.use_tags = True
        self.start_tag = start_tag
        self.end_tag = end_tag
        self.text_colors = {'default' : color.text_color}

        for color_name in color.color_names:
            self.text_colors[color_name] = color.colors[color_name]

        self.tag = Text.start_tag+'default'+Text.end_tag
        self.current_color = self.text_colors['default']
        self.scale_override = 1
        self._background = None
        self.appear_sequence = None # gets created when calling appear()

        if 'origin' in kwargs:   # set the scale before model for correct corners
            setattr(self, 'origin', kwargs['origin'])


        if text != '':
            self.text = text

        for key, value in kwargs.items():
            if key == 'origin':
                continue
            setattr(self, key, value)


    @property
    def text(self):
        t = ''
        y = 0
        if self.text_nodes:
            y = self.text_nodes[0].getY()

        for tn in self.text_nodes:
            if y != tn.getY():
                t += '\n'
                y = tn.getY()

            t += tn.node().text

        #Calls the render queue setter to make sure the text nodes render properly
        #This is so that the render queue will work when the text is changed
        self.render_queue=self.render_queue
        return t


    @text.setter     # set this to update the text.
    def text(self, text):
        self.raw_text = text

        # clear stuff
        from ursina.ursinastuff import destroy  # needed to destroy inline images
        for img in self.images:
            destroy(img)
        self.images = []

        for tn in self.text_nodes:
            tn.remove_node()
        self.text_nodes = []

        # check if using tags
        if (not self.use_tags
            or self.text == self.start_tag or self.text == self.end_tag
            or not self.start_tag in text or not self.end_tag in text
            ):

            self.create_text_section(text)
            self.align()
            return

        # parse tags
        text = self.start_tag + self.end_tag + str(text) # start with empty tag for alignment to work?
        sections = []
        section = ''
        tag = self.start_tag+'default'+self.end_tag
        temp_text_node = TextNode('temp_text_node')
        temp_text_node.setFont(self.font)
        x = 0
        y = 0

        i = 0
        while i < len(text):
            char = text[i]
            if char == '\n':
                sections.append([section, tag, x, y])
                section = ''
                y -= 1
                x = 0
                i += 1

            elif char == self.start_tag: # find tag
                sections.append([section, tag, x, y])
                x += temp_text_node.calcWidth(section)
                section = ''

                tag = ''
                for j in range(len(text)-i):
                    tag += text[i+j]
                    if text[i+j] == self.end_tag and len(tag) > 0:
                        i += j+1
                        break
            else:
                section += char
                i += 1

        sections.append([section, tag, x, y])

        for i, s in enumerate(sections):
            tag = s[1]
            # move the text after image one space right
            if tag.startswith(self.start_tag+'image:'):
                for f in sections:
                    if f[3] == s[3] and f[2] > s[2]:
                        f[2] += .5

                s[2] += .5

            self.create_text_section(text=s[0], tag=s[1], x=s[2], y=s[3])

        self.align()


    def create_text_section(self, text, tag='', x=0, y=0):
        # print(text, tag)
        self.text_node = TextNode('t')
        self.text_node_path = self.attachNewNode(self.text_node)
        try:
            self.text_node.setFont(self._font)
        except:
            pass    # default font


        if tag != '<>':
            tag = tag[1:-1]

            if tag.startswith('hsb('):   # set color based on numbers
                tag = tag[4:-1]
                hsb_values = tuple(float(e.strip()) for e in tag.split(','))
                self.current_color = color.color(*hsb_values)

            elif tag.startswith('rgb('):   # set color based on numbers
                tag = tag[4:-1]
                rgb_values = (float(e.strip()) for e in tag.split(','))
                self.current_color = color.rgba(*rgb_values)

            if tag.startswith('scale:'):
                scale = tag.split(':')[1]
                self.scale_override = float(scale)

            elif tag.startswith('image:'):
                texture_name = tag.split(':')[1]
                image = Entity(
                    parent=self.text_node_path,
                    name='inline_image',
                    model='quad',
                    texture=texture_name,
                    color=self.current_color,
                    # scale=self.scale_override,
                    # position=(x*self.size*self.scale_override, y*self.size*self.line_height),
                    origin=(.0, -.25),
                    add_to_scene_entities=False,
                    )
                if not image.texture:
                    destroy(image)
                else:
                    self.images.append(image)

            else:
                if tag in self.text_colors:
                    self.current_color = self.text_colors[tag]

        self.text_node_path.setScale(self.scale_override * self.size)
        self.text_node.setText(text)
        self.text_node.setTextColor(self.current_color)
        self.text_node.setPreserveTrailingWhitespace(True)
        # self.text_node_path.setPos(
        #     x * self.size * self.scale_override,
        #     0,
        #     (y * self.size * self.line_height) - .75 * self.size)
        self.text_node_path.setPos(
            x * self.size * self.scale_override,
            (y * self.size * self.line_height) - .75 * self.size,
            0)
        self.text_nodes.append(self.text_node_path)

        return self.text_node

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        font = loader.loadFont(value)
        if font:
            self._font = font
            self._font.clear()  # remove assertion warning
            self._font.setPixelsPerUnit(self.resolution)
            self._font.setLineHeight(self.line_height)
            self.text = self.raw_text   # update tex

    @property
    def color(self): # sets the default color.
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.current_color = value
        self.text_colors['default'] = value
        for tn in self.text_nodes:
            tn.node().setTextColor(value)
        for img in self.images:
            img.color = value


    @property
    def line_height(self):
        try:
            return self._line_height
        except:
            return 1

    @line_height.setter
    def line_height(self, value):
        self._line_height = value
        self._font.setLineHeight(value)
        if self.use_tags:
            self.text = self.raw_text

    @property
    def width(self): # gets the width of the widest line.
        if not hasattr(self, 'text'):
            return 0

        temp_text_node = TextNode('temp')
        temp_text_node.setFont(self._font)

        longest_line_length = 0
        for line in self.text.split('\n'):
            longest_line_length = max(longest_line_length, temp_text_node.calcWidth(line))

        return longest_line_length  * self.scale_x * self.size


    @property
    def height(self): # gets the height of the text
        return (len(self.lines) * self.line_height * self.scale_y * self.size)

    @property
    def lines(self):
        return self.text.splitlines()

    @property
    def resolution(self):
        return self._font.getPixelsPerUnit()

    @resolution.setter
    def resolution(self, value):
        self._font.setPixelsPerUnit(value)

    @property
    def wordwrap(self): # set this to make the text wrap after a certain number of characters.
        if hasattr(self, '_wordwrap'):
            return self._wordwrap
        else:
            return 0

    @wordwrap.setter
    def wordwrap(self, value):
        self._wordwrap = value
        if not value:
            return
            
        new_text = ''
        x = 0
        for word in self.raw_text.replace(self.end_tag, self.end_tag+' ').split(' '):

            if word.startswith(self.start_tag) and new_text:
                new_text = new_text[:-1]

            if not word.startswith(self.start_tag):
                x += len(word) + 1

            if x >= value:
                new_text += '\n'
                x = 0

            new_text += word + ' '

        self.text = new_text


    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        self._origin = value
        if self.text:
            self.text = self.raw_text

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, value):
        if value == True:
            self.create_background()
        elif self._background:
            from ursina.ursinastuff import destroy
            destroy(self._background)


    def align(self):
        value = self.origin

        linewidths = [self.text_nodes[0].node().calcWidth(line) for line in self.lines]
        # print('.........', linewidths)
        for tn in self.text_nodes:
            # center text horizontally
            # linenumber = abs(int(tn.getZ() / self.size / self.line_height))
            linenumber = abs(int(tn.getY() / self.size / self.line_height))
            tn.setX(tn.getX() - (linewidths[linenumber] / 2 * self.size * tn.getScale()[0] / self.size))
            # tn.setX(tn.getX() - (linewidths[linenumber] / 2 * self.size))
            # add offset based on origin/value
            # x -= half line width * text node scale
            tn.setX(
                tn.getX() - (linewidths[linenumber] / 2 * value[0] * 2 * self.size) * tn.getScale()[0] / self.size
                )
            # center text vertically
            halfheight = len(linewidths) * self.line_height / 2
            # tn.setZ(tn.getZ() + (halfheight * self.size))
            tn.setY(tn.getY() + (halfheight * self.size))
            # add offset
            # tn.setZ(tn.getZ() - (halfheight * value[1] * 2 * self.size))
            tn.setY(tn.getY() - (halfheight * value[1] * 2 * self.size))


    def create_background(self, padding=size*2, radius=size, color=ursina.color.black66):
        from ursina import Quad, destroy

        if self._background:
            destroy(self._background)

        self._background = Entity(parent=self, z=.01)

        if isinstance(padding, (int, float, complex)):
            padding = (padding, padding)

        w, h = self.width + padding[0], self.height + padding[1]
        self._background.x -= self.origin_x * self.width
        # if self.origin_x == .5:
        #     self._background.x += self.origin_x * self.width * 2
        self._background.y -= self.origin_y * self.height

        self._background.model = Quad(radius=radius, scale=(w/self.scale_x, h/self.scale_y))
        self._background.color = color


    def appear(self, speed=.025, delay=0):
        from ursina.ursinastuff import invoke
        self.enabled = True
        # self.visible = True   # setting visible seems to reset the colors
        if self.appear_sequence:
            self.appear_sequence.finish()

        x = 0
        self.appear_sequence = Sequence()
        for i, tn in enumerate(self.text_nodes):
            target_text = tn.node().getText()
            tn.node().setText('')
            new_text = ''

            for j, char in enumerate(target_text):
                new_text += char
                self.appear_sequence.append(Wait(speed))
                self.appear_sequence.append(Func(tn.node().setText, new_text))

        self.appear_sequence.start()
        return self.appear_sequence


    def get_width(string, font=None):
        t = Text(string)
        if font:
            t.font = font
        w = t.width
        from ursina import destroy
        destroy(t)
        return w



if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    # Text.size = .001
    descr = dedent('''
        Rainstorm
        Summon a rain storm to deal 5 water

        damage to everyone, test including yourself.
        1234 1234 1234 1234 1234 1234 2134 1234 1234 1234 1234 1234 2134 2134 1234 1234 1234 1234
        Lasts for 4 rounds.''').strip()

    # Text.default_font = 'VeraMono.ttf'
    # Text.default_font = 'consola.ttf'
    # color.text_color = color.lime
    Text.default_resolution = 1080 * Text.size
    test = Text(text=descr, wordwrap=30)
    # test.align()
    # test = Text(descr)

    # test.text = ''
    # print(test.images)
  # print('\n', test.text, '\n\n')
    # test.font = 'VeraMono.ttf'
    # Text.font = 'VeraMono.ttf'
    # test.origin = (.5, .5)
    # test.origin = (0, 0)
    # test.wordwrap = 40

    # text = Text(text=descr, wordwrap=10, origin=(-.5,.5), y=.25, background=True)
    # Entity(parent=camera.ui, model='circle', scale=.05, color=color.yellow, y=text.y, z=-1)


    def input(key):
        if key == 'a':
            # test.appear(speed=.025)
            print('a')
            test.text = '<default><image:file_icon> <red><image:file_icon> test '
            print('by', test.text)

    # test.create_background()
    window.fps_counter.enabled = False
    print('....', Text.get_width('yolo'))
    app.run()