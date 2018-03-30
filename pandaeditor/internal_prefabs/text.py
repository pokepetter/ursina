import sys
import time
sys.path.append("..")
from pandaeditor import *
from panda3d.core import TransparencyAttrib

from os import path
from panda3d.core import Filename
from panda3d.core import TextNode
import textwrap

from pandaeditor.entity import Entity

class Text(Entity):

    def __init__(self, text=None):
        super().__init__()
        self.name = 'text'
        self.scale *= 0.25 * scene.editor_font_size
        self.origin = (0, 0)

        self.setColorScaleOff()
        self.text_nodes = list()
        self.align = 'left'
        # self.font = 'VeraMono.ttf'
        temp_text_node = TextNode('')
        self._font = temp_text_node.getFont()

        self.line_height = 1

        self.text_colors = {
            '<default>' : color.text_color,
            '<white>' : color.white,
            '<smoke>' : color.smoke,
            '<light_gray>' : color.light_gray,
            '<gray>' : color.gray,
            '<dark_gray>' : color.dark_gray,
            '<black>' : color.black,

            '<red>' : color.red,
            '<orange>' : color.orange,
            '<yellow>' : color.yellow,
            '<lime>' : color.lime,
            '<green>' : color.green,
            '<turquoise>' : color.turquoise,
            '<cyan>' : color.cyan,
            '<azure>' : color.azure,
            '<blue>' : color.blue,
            '<violet>' : color.violet,
            '<magenta>' : color.magenta,
            '<pink>' : color.pink,
            }

        self.tag = '<default>'
        self.color = self.text_colors['<default>']
        self.scale_override = 1

        if text:
            self.text = text
            # self.line_height = 1


    @property
    def text(self):
        t = ''
        y = 0
        for tn in self.text_nodes:
            if y != tn.getZ():
                t += '\n'
            t += tn.node().text

        return t


    @text.setter
    def text(self, text):
        self.raw_text = text
        text = str(text)
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
                if len(section) > 0:
                    sections.append([section, tag, x, y])
                    section = ''
                y -= 1
                x = 0
                i += 1

            elif char == '<': # find tag
                if len(section) > 0:
                    sections.append([section, tag, x, y])
                    x += temp_text_node.calcWidth(section)
                    section = ''

                tag = ''
                for j in range(len(text)-i):
                    tag += text[i+j]
                    if text[i+j] == '>':
                        i += j+1
                        break
            else:
                section += char
                i += 1

        sections.append([section, tag, x, y])

        for s in sections:
            # print('---', s)
            self.create_text_section(text=s[0], tag=s[1], x=s[2], y=s[3])


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
        self.text_node_path.setPos(x * self.scale_override, 0, y * self.line_height)
        self.text_nodes.append(self.text_node_path)

        if tag in self.text_colors:
            lightness = color.to_hsv(self.color)[2]
            self.color = self.text_colors[tag]
            if not tag == '<default>':
                if lightness > .8:
                    self.color = color.tint(self.color, .2)
                else:
                    self.color = color.tint(self.color, -.3)

            self.text_node.setTextColor(self.color)

        elif tag.startswith('<scale:'):
            scale = tag.split(':')[1]
            self.scale_override = scale = float(scale[:-1])

        self.text_node_path.setScale(self.scale_override)


        return self.text_node

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        self._font = loader.loadFont(value)
        # _font.setRenderMode(TextFont.RMPolygon)
        self._font.setPixelsPerUnit(50)
        print('FONT FILE:', self._font)
        for tn in self.text_nodes:
            tn.setFont(self._font)

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
        longest_line = ''
        for line in self.text.split('\n'):
            if len(line) > len(longest_line):
                longest_line = line

        temp_text_node = TextNode(longest_line)
        temp_text_node.setFont(self.font)
        return temp_text_node.calcWidth(longest_line)  * self.scale_x


    @property
    def height(self):
        return len(self.raw_text.split('\n')) * self.line_height * self.scale_y


    @property
    def wordwrap(self):
        if hasattr(self, '_wordwrap'):
            return self._wordwrap
        else:
            return 0

    @wordwrap.setter
    def wordwrap(self, value):
        self._wordwrap = value

        newstring = ''
        words = [w for w in self.raw_text.replace('>', '> ').split(' ')]
        linelength = 0
        for i, w in enumerate(words):
            if linelength + len(w) + 1 > value:
                newstring += w + '\n'
                linelength = 0
            elif not w.startswith('<'): # don't count tags
                newstring += w + ' '
                linelength += len(w) + 1
            else:
                newstring += w

        self.text = newstring



    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except:
            pass

        if name == 'align':
            object.__setattr__(self, name, value)
            if value == 'left':
                for tn in self.text_nodes:
                    tn.node().setAlign(TextNode.ALeft)
            elif value == 'center':
                for tn in self.text_nodes:
                    tn.node().setAlign(TextNode.ACenter)
            elif value == 'right':
                for tn in self.text_nodes:
                    tn.node().setAlign(TextNode.ARight)




if __name__ == '__main__':
    app = PandaEditor()
    origin = Entity()
    origin.model = 'quad'
    origin.scale *= .01

    descr = '''
Increase max health with 25% <scale:1.5> and
raise attack with
<scale:1>100 for 2 turns.
'''
    descr = descr.strip()
    replacements = {
        'hp' : '<red>hp<default>',
        'max health' : '<red>max health<default>',
        'attack' : '<orange>attack<default>'
    }
    descr = multireplace(descr, replacements)
    test = Text(descr)

    # test.font = 'VeraMono.ttf'
#     test.text = '''
# <lime>*If <default>target has more than <red>50% hp, <default>*burn the enemy for 5 * INT fire damage for 3 turns. <yellow>Else, deal 100 damage. <default>Unfreezes target. Costs <blue>10 mana.
# '''.strip()
    test.wordwrap = 30
    # test.text = '<red>yolo<green>'
    # test.line_height = 4

    app.run()
