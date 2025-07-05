from panda3d.core import TextNode
from panda3d.core import FontPool
from panda3d.core import Filename

import builtins
import re
import sys

import ursina
from ursina import camera
from ursina import application
from ursina.entity import Entity
from ursina.sequence import Sequence, Func, Wait
from ursina import color
from ursina import destroy
from ursina.shaders.text_shader import text_shader
from ursina.string_utilities import print_warning
from ursina.scripts.property_generator import generate_properties_for_class
# note:
# <scale:n> tag doesn't work well in the middle of text.
# only good for titles for now.

from functools import lru_cache
@lru_cache()
def _search_for_file(name, folders, file_types=None): # prioritizes based on file_type order, then folder order.
    if file_types is None and '.' not in name:
        raise Exception(f'name({name}) has no file type, and no file_types were provided.')

    if '.' in name:
        file_types = ('', )

    for file_type in file_types:
        for folder in folders:
            # print('-----', 'searchpattern:', f'{folder}/**/{name}{file_type}', 'result:', list(folder.glob(f'**/{name}.{file_type}')))
            for file_path in folder.glob(f'**/{name}{file_type}'):
                #print('FOUND FONT:', file_path)
                return file_path

    return None


@generate_properties_for_class()
class Text(Entity):
    size = .025
    default_font = 'OpenSans-Regular.ttf'
    default_monospace_font = 'VeraMono.ttf'
    default_resolution = 1080 * size * 2
    start_tag = '<'
    end_tag = '>'

    def __init__(self, text='', start_tag=start_tag, end_tag=end_tag, ignore=True, **kwargs):
        super().__init__(ignore=ignore)
        self.size = Text.size
        self.parent = camera.ui

        self.setColorScaleOff()
        self.text_nodes = []
        self.images = []
        self.origin = (-.5, .5)

        self.font = Text.default_font
        self.shader = text_shader
        self.shader.compile()
        self.resolution = Text.default_resolution
        self.use_tags = True
        self.line_height = 1
        self.start_tag = start_tag
        self.end_tag = end_tag
        self.text_colors = {'default' : color.text_color}
        self.color = color.text_color

        for color_name in color.color_names:
            self.text_colors[color_name] = color.colors[color_name]

        self.tag = Text.start_tag + 'default' + Text.end_tag
        self.current_color = self.text_colors['default']
        self.scale_override = 1
        self._background = None
        self.appear_sequence = None # gets created when calling appear()


        if 'origin' in kwargs:   # set the scale before model for correct corners
            setattr(self, 'origin', kwargs['origin'])
        if 'use_tags' in kwargs:
            setattr(self, 'use_tags', kwargs['use_tags'])

        if text != '':
            self.text = text

        for key, value in kwargs.items():
            if key == 'origin':
                continue
            setattr(self, key, value)




    def text_getter(self):
        t = ''
        y = 0
        if self.text_nodes:
            y = self.text_nodes[0].getY()

        for tn in self.text_nodes:
            if y != tn.getY():
                t += '\n'
                y = tn.getY()

            t += tn.node().text

        return t


    def text_setter(self, text): # set this to update the text.
        self.raw_text = text

        # clear stuff
        for img in self.images:
            destroy(img)
        self.images = []

        for tn in self.text_nodes:
            tn.remove_node()
        self.text_nodes = []
        if not text:
            return

        # check if using tags
        if (not self.use_tags
            # or self.text == self.start_tag or self.text == self.end_tag
            # or not self.start_tag in text or not self.end_tag in text
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
        if self.font is not None:
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
                done = False
                for j in range(len(text)-i):
                    tag += text[i+j]
                    if text[i+j] == self.end_tag and len(tag) > 0:
                        i += j+1
                        done = True
                        break
                if not done:
                    i += 1
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

            if tag.startswith('hsv('):   # set color based on numbers
                tag = tag[4:-1]
                hsb_values = tuple(float(e.strip()) for e in tag.split(','))
                self.current_color = color.hsv(*hsb_values)

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
                    shader=None,
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

        self.text_node_path.setShader(self.shader._shader)
        for key, shader_input in self.shader.default_input.items():
            self.text_node_path.setShaderInput(key, shader_input)

        self.text_node_path.setPos(
            x * self.size * self.scale_override,
            (y * self.size * self.line_height) - .75 * self.size,
            0)
        self.text_nodes.append(self.text_node_path)

        return self.text_node

    def font_getter(self):
        return getattr(self, '_font', None)

    def font_setter(self, value):
        font_file_types = ('.ttf', '.otf') if '.' not in value else ('', )
        folders = (application.fonts_folder, application.asset_folder, application.internal_fonts_folder)
        font_file_path = _search_for_file(value, folders, font_file_types)

        if not font_file_path:
            print_warning('missing font:', value)

        if sys.platform == 'linux':
            font = FontPool.load_font(str(font_file_path))
        else:
            font = FontPool.load_font(str(font_file_path.name))

        if font:
            self._font = font
            self._font.clear()  # remove assertion warning
            self._font.setPixelsPerUnit(self.resolution)
            self._font.setLineHeight(self.line_height)
            if self.text:
                self.text = self.raw_text   # update tex


    def color_setter(self, value):
        self._color = value
        self.current_color = value
        self.text_colors['default'] = value
        for tn in self.text_nodes:
            tn.node().setTextColor(value)
        for img in self.images:
            img.color = value


    def shader_setter(self, value):
        self._shader = value
        if not hasattr(self, 'text_nodes'): # trying to set shader before init has finish, for example by using Entity.default_shader
            return

        for tn in self.text_nodes:
            tn.setShader(value._shader)
            for key, shader_input in value.default_input.items():
                tn.setShaderInput(key, shader_input)


    def line_height_getter(self):
        return getattr(self, '_line_height', 1)

    def line_height_setter(self, value):
        self._line_height = value
        if self.font is None:
            return
        if self.use_tags and self.text:
            self.text = self.raw_text
        else:
            self._font.setLineHeight(value)

    @property
    def width(self): # gets the width of the widest line.
        if not hasattr(self, 'text'):
            return 0

        temp_text_node = TextNode('temp')
        if self.font is None:
            print_warning('font not loaded, so Text.width may be wrong')
            return 1
        temp_text_node.setFont(self._font)

        longest_line_length = 0
        for line in self.text.split('\n'):
            longest_line_length = max(longest_line_length, temp_text_node.calcWidth(line))

        return longest_line_length * self.size


    @property
    def height(self): # gets the height of the text
        return (len(self.lines) * self.line_height * self.size)

    @property
    def lines(self):
        return self.text.splitlines()

    def resolution_getter(self):
        return self._font.getPixelsPerUnit()

    def resolution_setter(self, value):
        if self.font is None:
            return
        self._font.setPixelsPerUnit(value)


    def wordwrap_setter(self, value):   # set this to make the text wrap after a certain number of characters.
        self._wordwrap = value
        if not value:
            return

        new_text = ''
        for line in self.raw_text.split('\n'):
            x = 0
            for word in line.split(' '):
                clean_string = re.sub('<.*?>', '', word)
                x += len(clean_string) + 1
                # print('w:', word, 'len:', len(clean_string), 'clean str:', clean_string)

                if x >= value:
                    new_text += '\n'
                    x = 0

                new_text += word + ' '

            new_text += '\n'

        self.text = new_text


    def origin_setter(self, value):
        self._origin = value
        if self.text:
            self.text = self.raw_text


    def background_setter(self, value):
        if value is True:
            self.create_background()
        elif self._background:
            from ursina.ursinastuff import destroy
            destroy(self._background)


    def align(self):
        value = self.origin

        linewidths = [self.text_nodes[0].node().calcWidth(line) for line in self.lines]
        for tn in self.text_nodes:
            # center text horizontally
            # linenumber = abs(int(tn.getZ() / self.size / self.line_height))
            linenumber = abs(int(tn.getY() / self.size / self.line_height))
            linenumber = clamp(linenumber, 0, len(linewidths)-1)

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

        self._background.model = Quad(radius=radius, scale=(w, h))
        self._background.color = color


    def appear(self, speed=.025):   # make the text animate in, one character at a time
        self.enabled = True
        # self.visible = True   # setting visible seems to reset the colors
        if self.appear_sequence:
            self.appear_sequence.finish()

        self.appear_sequence = Sequence()
        for tn in self.text_nodes:
            target_text = tn.node().getText()
            tn.node().setText('')
            new_text = ''

            for char in target_text:
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
    from ursina import Ursina, dedent, window
    app = Ursina()
    # Text.size = .001
    descr = dedent('''
        <red>Rainstorm<default> <red>Rainstorm<default>
        Summon a rain storm to deal 5 <blue>water<default> damage to everyone, test including yourself.
        1234 1234 1234 1234 1234 1234 2134 1234 1234 1234 1234 1234 2134 2134 1234 1234 1234 1234
        Lasts for 4 rounds.''').strip()

    # Text.default_font = 'VeraMono.ttf'
    # Text.default_font = 'consola.ttf'
    # color.text_color = color.lime
    Text.default_resolution = 1080 * Text.size
    test = Text(text=descr, wordwrap=30, scale=4)


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

        if key == 'c':
            test.text = ''
    # test.create_background()
    Sky(color=color.dark_gray)
    EditorCamera()
    window.fps_counter.enabled = False
    print('....', Text.get_width('yolo'))
    app.run()