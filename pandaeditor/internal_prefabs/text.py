import sys
import time
sys.path.append("..")
from pandaeditor import *
from panda3d.core import TransparencyAttrib

from os import path
from panda3d.core import Filename
from panda3d.core import TextNode

from pandaeditor.entity import Entity

class Text(Entity):

    def __init__(self, text_arg=None):
        super().__init__()
        self.name = 'text'
        self.scale *= 0.25 * scene.editor_font_size
        self.origin = (0, 0)

        self.text_node = TextNode('node name')
        self.font = 'font/VeraMono.ttf'
        self.text_node_path = self.attachNewNode(self.text_node)

        self.setColorScaleOff()
        self.color = color.text
        self.align = 'left'
        self.use_tags = True

        # temp
        # self.text_node.setFrameColor(1, 1, 1, 1)
        # self.text_node.setFrameAsMargin(0.5, 0.5, 0.5, 0.5)

        self.color = color.text_color
        self.text_node_path.setLightOff()
        self.text_node_path.setBin("fixed", 0)
        self.text_node.setPreserveTrailingWhitespace(True)

        self.text_colors = {    # I use custom colors because pure colors doesn't look too good on text
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

        if text_arg:
            self.text = text_arg

    def update_text(self):
        pass

    def appear(self, interval):
        for char in self.characters:
            char.node_path


    @property
    def text(self):
        return self.text_node.getText()


    @text.setter
    def text(self, text):
        if not self.use_tags:
            self.text_node.setText(value)
            return

        sections = list()
        section = ''
        tag = '<default>'
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
                    x += self.text_node.calcWidth(section)
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


    def create_text_section(self, text, tag, x, y):
        self.text_node = TextNode('t')
        self.text_node_path = self.attachNewNode(self.text_node)
        self.text_node.setText(text)
        self.text_node.setPreserveTrailingWhitespace(True)
        self.text_node_path.setPos(x, 0, y)

        if tag in self.text_colors:
            lightness = color.to_hsv(self.color)[2]
            c = self.text_colors[tag]
            if lightness > .8:
                c = color.tint(c, .2)
            else:
                c = color.tint(c, -.3)

            self.text_node.setTextColor(c)


    @property
    def font(self):
        return self.text_node.getFont()

    @font.setter
    def font(self, value):
        # try:
        font_file = loader.loadFont(value)
        # font_file.setRenderMode(TextFont.RMPolygon)
        font_file.setPixelsPerUnit(50)
        self.text_node.setFont(font_file)
        object.__setattr__(self, name, value)
        # except:
        #     print('no font called:', value)


    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except:
            pass

        if name == 'align':
            object.__setattr__(self, name, value)
            if value == 'left':
                self.text_node.setAlign(TextNode.ALeft)
            elif value == 'center':
                self.text_node.setAlign(TextNode.ACenter)
            elif value == 'right':
                self.text_node.setAlign(TextNode.ARight)

        if name == 'color':
            object.__setattr__(self, name, value)
            try:
                self.text_node.setTextColor(value)
            except:
                pass

        if name == 'wordwrap':
            object.__setattr__(self, name, value)
            print('set wordwrap to:', value)
            self.text_node.setWordwrap(value)
            print('yay')



if __name__ == '__main__':
    app = PandaEditor()
    origin = Entity()
    origin.model = 'quad'
    origin.scale *= .01
    test = Text('''
<lime>*If <default>target has more than <red>50% hp,
<default>*burn the enemy for 5 * INT fire damage
*for 3 turns. <yellow>Else, deal 100 damage.
*Unfreezes target. Costs <blue>10 mana.
'''.strip().strip())
    # print(test.text_colors['<red>'])
    # test.text = 'test text'
    app.run()
