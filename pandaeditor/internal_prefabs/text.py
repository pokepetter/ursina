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

        self.setColorScaleOff()
        self.text_nodes = list()
        self.align = 'left'

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

        if text_arg:
            self.text = text_arg


    @property
    def text(self):
        return ''.join([tn for tn in self.text_nodes])


    @text.setter
    def text(self, text):
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
        self.text_node.setText(text)
        self.text_node.setPreserveTrailingWhitespace(True)
        self.text_node_path.setPos(x, 0, y)
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

        return self.text_node

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
                for tn in self.text_nodes:
                    tn.node().setAlign(TextNode.ALeft)
            elif value == 'center':
                for tn in self.text_nodes:
                    tn.node().setAlign(TextNode.ACenter)
            elif value == 'right':
                for tn in self.text_nodes:
                    tn.node().setAlign(TextNode.ARight)


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
'''.strip())

    # test.text = '452 <red>some random text'
    app.run()
