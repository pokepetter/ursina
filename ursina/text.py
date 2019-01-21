import sys
import time
import ursina
from ursina import *
from panda3d.core import TransparencyAttrib

from os import path
from panda3d.core import Filename
from panda3d.core import TextNode
import textwrap

from ursina.entity import Entity

# note:
# <scale:n> tag doesn't work well in the middle of text.
# only good for titles for now.

class Text(Entity):

    size = .025

    def __init__(self, text=None, **kwargs):
        super().__init__()
        self.name = 'text'
        self.size = Text.size
        self.parent = camera.ui

        self.setColorScaleOff()
        self.text_nodes = list()
        self.origin = (-.5, .5)
        # self.font = 'VeraMono.ttf'
        temp_text_node = TextNode('')
        self._font = temp_text_node.getFont()

        self.line_height = 1

        self.text_colors = {'<default>' : color.text_color}

        for color_name in color.color_names:
            self.text_colors['<' + color_name + '>'] = color.colors[color_name]

        self.tag = '<default>'
        self.color_tag = self.text_colors['<default>']
        self.scale_override = 1
        self.background = None

        if text:
            self.text = text
        #     # self.line_height = 1
        for key, value in kwargs.items():
            setattr(self, key, value)


    @property
    def text(self):
        t = ''
        y = 0
        for tn in self.text_nodes:
            if y != tn.getZ():
                t += '\n'
                y = tn.getZ()
            t += tn.node().text

        return t


    @text.setter
    def text(self, text):
        self.raw_text = text
        text = '<>' + str(text)
        for tn in self.text_nodes:
            tn.remove_node()
        self.text_nodes.clear()

        if not '<' in text:
            self.create_text_section(text)
            return

        sections = list()
        section = ''
        tag = '<default>'
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

            elif char == '<': # find tag
                sections.append([section, tag, x, y])
                x += temp_text_node.calcWidth(section)
                section = ''

                tag = ''
                for j in range(len(text)-i):
                    tag += text[i+j]
                    if text[i+j] == '>' and len(tag) > 0:
                        i += j+1
                        break
            else:
                section += char
                i += 1

        sections.append([section, tag, x, y])

        for s in sections:
            # print('---', s)
            self.create_text_section(text=s[0], tag=s[1], x=s[2], y=s[3])

        # self.origin = self.origin   # recalculate text alignment after assigning new text
        self.align()

    def update_text(self):
        self.text = self.raw_text

    def create_text_section(self, text, tag='<default>', x=0, y=0):
        self.text_node = TextNode('t')
        self.text_node_path = self.attachNewNode(self.text_node)
        try:
            self.text_node.setFont(self._font)
        except:
            print('default font')
            pass    # default font
        self.text_node.setText(text)
        self.text_node.setPreserveTrailingWhitespace(True)
        self.text_node_path.setPos(
            x * self.size * self.scale_override,
            0,
            (y * self.size * self.line_height) - .75 * self.size)
        if not text == '':
            self.text_nodes.append(self.text_node_path)

        if tag in self.text_colors:
            lightness = color.to_hsv(self.color_tag)[2]
            self.color_tag = self.text_colors[tag]
            if not tag == '<default>':
                if lightness > .8:
                    self.color_tag = color.tint(self.color_tag, .2)
                else:
                    self.color_tag = color.tint(self.color_tag, -.3)

            self.text_node.setTextColor(self.color_tag)

        if tag.startswith('<scale:'):
            scale = tag.split(':')[1]
            self.scale_override = scale = float(scale[:-1])

        self.text_node_path.setScale(self.scale_override * self.size)


        return self.text_node

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        self._font = loader.loadFont(value)
        # _font.setRenderMode(TextFont.RMPolygon)
        self._font.setPixelsPerUnit(100)
        # print('FONT FILE:', self._font)
        self.text = self.raw_text   # update text

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        for tn in self.text_nodes:
            tn.node().setTextColor(value)

    @property
    def line_height(self):
        try:
            return self._line_height
        except:
            return 1

    @line_height.setter
    def line_height(self, value):
        self._line_height = value
        self.text = self.raw_text

    @property
    def width(self):
        if not hasattr(self, 'text'):
            return 0

        temp_text_node = TextNode('temp')
        temp_text_node.setFont(self.font)

        longest_line_length = 0
        for line in self.text.split('\n'):
            longest_line_length = max(longest_line_length, temp_text_node.calcWidth(line))

        return longest_line_length  * self.scale_x * self.size


    @property
    def height(self):
        return (len(self.lines) * self.line_height * self.scale_y * self.size)

    @property
    def lines(self):
        return [l for l in self.text.split('\n') if len(l) > 0]


    @property
    def wordwrap(self):
        if hasattr(self, '_wordwrap'):
            return self._wordwrap
        else:
            return 0

    @wordwrap.setter
    def wordwrap(self, value):
        self._wordwrap = value

        linelength = 0
        newstring = ''
        i = 0
        while i < (len(self.raw_text)):
            char = self.raw_text[i]

            if char == '<':
                for j in range(len(self.raw_text) - i):
                    if self.raw_text[i+j] == '>':
                        break
                    newstring += self.raw_text[i+j]
                i += j + 0  # don't count tags

            else:
                if char == '\n':
                    linelength = 0

                # find length of word
                for l in range(min(100, len(self.raw_text) - i)):
                    if self.raw_text[i+l] == ' ':
                        break

                if linelength + l > value:  # add linebreak
                    newstring += '\n'
                    linelength = 0

                newstring += char
                linelength += 1
                i += 1

        newstring = newstring.replace('\n>', '>\n')
        # print('--------------------\n', newstring)
        self.text = newstring


    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        self._origin = value
        if self.text:
            self.text = self.raw_text

    def align(self):
        value = self.origin
        linewidths = [self.text_nodes[0].node().calcWidth(line) for line in self.lines]
        for tn in self.text_nodes:
            # center text horizontally
            linenumber = abs(int(tn.getZ() / self.size / self.line_height))
            tn.setX(tn.getX() - (linewidths[linenumber] / 2 * self.size * tn.getScale()[0] / self.size))
            # add offset based on origin/value
            # x -= half line width * text node scale
            tn.setX(
                tn.getX()
                - (linewidths[linenumber] / 2 * value[0] * 2 * self.size)
                * tn.getScale()[0] / self.size
                )
            # center text vertically
            halfheight = len(linewidths) * self.line_height / 2
            tn.setZ(tn.getZ() + (halfheight * self.size))
            # add offset
            tn.setZ(tn.getZ() - (halfheight * value[1] * 2 * self.size))

        if hasattr(self, '_background'):
            self._background.origin = value


    def create_background(self, padding=size*2, radius=size, color=ursina.color.black66):
        from ursina import Quad, destroy

        if self.background:
            destroy(self.background)

        self.background = Entity(parent=self, z=.01)

        if isinstance(padding, (int, float, complex)):
            padding = (padding, padding)

        w, h = self.width + padding[0], self.height + padding[1]
        self.background.x -= self.origin_x * self.width
        self.background.y -= self.origin_y * self.height

        self.background.model = Quad(radius=radius, scale=(w, h))
        self.background.color = color


    def appear(self):
        for i, tn in enumerate(self.text_nodes):
            tn.setX(tn.getX()-999999)

        speed = .025

        x = 0
        for i, tn in enumerate(self.text_nodes):
            target_text = tn.node().getText()
            print(target_text)
            invoke(tn.setX, tn.getX()+999999, delay=(i+x)*speed)

            new_text = ''
            for j, char in enumerate(target_text):
                # print(char)
                new_text += char
                invoke(tn.node().setText, new_text, delay=(i+x+j)*speed)

            x += len(target_text)


if __name__ == '__main__':
    app = Ursina()
    descr = ('<scale:1.5><orange>' + 'Rainstorm' + '<scale:1>\n' +
'''Summon a <azure>rain storm <default>to deal 5 <azure>water
damage <default>to <red>everyone, <default>including <orange>yourself. <default>
Lasts for 4 rounds.''')
    test = Text(descr)
#     # print('\n', test.text, '\n\n')
    test.font = 'VeraMono.ttf'
    # test.origin = (.5, .5)
    # test.origin = (0, 0)
    # test.wordwrap = 40
    test.create_background()

    app.run()
