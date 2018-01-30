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
        self.html_tags = True

        # temp
        # self.text_node.setFrameColor(1, 1, 1, 1)
        # self.text_node.setFrameAsMargin(0.5, 0.5, 0.5, 0.5)

        self.color = color.text_color
        self.text_node_path.setLightOff()
        self.text_node_path.setBin("fixed", 0)
        self.text_node.setPreserveTrailingWhitespace(True)

        if text_arg:
            self.text = text_arg

        self.style_tags = (
            '<bold>',
            '<red>',
            '<green>'
            )


    def update_text(self):
        pass

    def appear(self, interval):
        for char in self.characters:
            char.node_path


    @property
    def text(self):
        return self.text_node.getText()

    @text.setter
    def text(self, value):
        # print('--------------set text', value)
        # self.text_node.setText(str(value))

        # import string
        # punc = string.punctuation

        # thestring = "Hey, you - what are you doing here!?"
        # s = list(value)
        # ''.join([o for o in s if not o in self.style_tags]).split()
        # s = ''.join([c for c in value])
        # words =
        import re
        value = re.split('<red>|<green>|<blue>', value)

        self.text_nodes = list()
        # self.text_nodes.append(self.text_node)

        cumulative_width = 0
        cumulative_y = 0

        for i, t in enumerate(value):
            print(t)
            self.text_node = TextNode(t)
            self.text_node_path = self.attachNewNode(self.text_node)
            self.text_node.setText(t)
            self.text_node.setPreserveTrailingWhitespace(True)
            self.text_node.setTextColor(color.color(i * 30, 1, .8))
            # print('________', self.font.getSpaceAdvance())

            self.text_node_path.setX(cumulative_width)
            self.text_node_path.setZ(-cumulative_y)


            if i > 0:
                if value[i-1].count('\n') > 0:
                     cumulative_width = 0
                     cumulative_y += value[i-1].count('\n')

            cumulative_width += self.text_node.getWidth()
            print(cumulative_width, cumulative_y)
            # a = Text(t)
            # self.text_nodes.append(Text(str(t)))
        # s = value.split('<red>')

        # for v in value:
        #     print(v)
        # print('____________', value)

        # else:
        #     print('no', '<red>', 'in string')
            # value.split('''<red>''')


        # print(value)

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
    test = Text('''
test. <red>Hey there!
wahzzup?
''')
    # test.text = 'test text'
    app.run()
