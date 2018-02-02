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



    def create_text_section(self, text, x, y):
        if len(text) == 0:
            return

        # print('create text:', text)
        self.text_node = TextNode(text)
        self.text_node_path = self.attachNewNode(self.text_node)
        self.text_node.setText(text)
        self.text_node.setPreserveTrailingWhitespace(True)
            #     # self.text_node_path.setY(i * .1)
        self.text_node_path.setPos(x, 0, y)

    @text.setter
    def text(self, text):
        if not self.use_tags:
            self.text_node.setText(value)
            return

        sections = list()
        section = ''
        prev_text = ''
        x_pos = 0
        y_pos = 0


        i = 0
        while i < len(text)-1:
            # print(text[i])
            char = text[i]
            # section = ''
            if char == '\n' and text[i+1] != '<':
                print('nn:', section)
                self.create_text_section(section, 0, y_pos)
                x_pos = 0
                y_pos -= 1
                section = ''
                i += 1
            elif char == '<': # find tag
                next_tag = ''
                for j in range(len(text)-i):
                    next_tag += text[i+j]
                    if text[i+j] == '>':
                        i += j+1
                        break

                x_pos += self.text_node.calcWidth(prev_text)
                y_pos -= 1
                self.create_text_section(section, x_pos, y_pos)
                self.tag = next_tag
                # print('next tag is:', next_tag, section)
                print('cc:', section)
                prev_text = section
                section = ''
            else:
                section += char
                i += 1

        print(section)

        # prev_x = 0
        # prev_y = 0
        #
        # for i, t in enumerate(final):
        #     print('t:', t)
        #     if i > 0:
        #         # prev_x = self.text_node_path.getX()
        #         # print('l:', list(final.keys())[i-1])
        #         # print(self.text_node.calcWidth(list(final.keys())[i-1].split('\n')[-1]))
        #         # prev_x += self.text_node.getRight()
        #         prev_x = self.text_node.calcWidth(list(final.keys())[-1])
        #         # prev_x = 0
        #         # prev_y = self.text_node_path.getZ()
        #
        #         prev_y = -self.text_node.getLineHeight() * cumulative_text.count('\n')
        #         if value[i-1].endswith('\n'):
        #             prev_x = 0
        #
        #     cumulative_text += t
        #         #     prev_y -= 1
        #         # if '\n' in value[i-1]:
        #         #     prev_y -= value[i-1].count('\n')
        #         #     prev_x = 0
        #
        #     self.text_node = TextNode(t)
        #     self.text_node_path = self.attachNewNode(self.text_node)
        #     self.text_node.setText(t)
        #     self.text_node.setPreserveTrailingWhitespace(True)
        #     # self.text_node_path.setY(i * .1)
        #     self.text_node_path.setPos(prev_x, 0, prev_y)
        #
        #     if final[t] in self.text_colors:
        #         lightness = color.to_hsv(self.color)[2]
        #         c = self.text_colors[final[t]]
        #         if lightness > .8:
        #             c = color.tint(c, .2)
        #         else:
        #             print('DDAAAARRRKKK')
        #             c = color.tint(c, -.3)
        #
        #         self.text_node.setTextColor(c)

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
<lime>If <default>target has more than <red>50% hp,
<default>burn the enemy for 5 * INT fire damage
for 3 turns. <yellow>Else, deal 100 damage.
Unfreezes target. Costs <blue>10 mana.
'''.strip().strip())
    # print(test.text_colors['<red>'])
    # test.text = 'test text'
    app.run()
