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

    def __init__(self, text=None):
        super().__init__()
        self.name = 'text'
        # self.character_spacing = .5
        # self.line_height = 1
        # self.character_limit = 50
        # self.characters = list()
        self.scale *= 0.25 * scene.editor_font_size
        self.origin = (0, 0)

        self.text_node = TextNode('node name')
        self.font = 'font/VeraMono.ttf'
        # self.text_node.setText("Every day in every way I'm getting better and better.")
        self.text_node_path = self.attachNewNode(self.text_node)

        self.setColorScaleOff()
        self.color = color.text
        self.align = 'left'

        # temp
        # self.text_node.setFrameColor(1, 1, 1, 1)
        # self.text_node.setFrameAsMargin(0.5, 0.5, 0.5, 0.5)

        self.color = color.text_color
        self.text_node_path.setLightOff()
        self.text_node_path.setBin("fixed", 0)

        # align = 0: top, 1: center, 2:bottom
        # bounds = self.getTightBounds()
        # z = 1 - bounds[1][2]
        # z = -(bounds[1] + bounds[0])[2] * .5
        # z = -bounds[0][2] -1

        z = -.3
        self.text_node_path.setZ(z)

        if text:
            self.text = text


    def update_text(self):
        pass

    def appear(self, interval):
        for char in self.characters:
            char.node_path

    def update_colors(self, value):
        if hasattr(self, 'characters'):
            print('updating colors')
            for char in self.characters:
                char.color = value


    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except:
            pass

        if name == 'text':
            object.__setattr__(self, name, value)
            self.text_node.setText(str(value))

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

        if name == 'font':
            try:
                font_file = loader.loadFont(value)
                # font_file.setRenderMode(TextFont.RMPolygon)
                font_file.setPixelsPerUnit(50)
                self.text_node.setFont(font_file)
            except:
                print('no font called:', value)

if __name__ == '__main__':
    app = PandaEditor()
    test = Text('test')
    # test.text = 'test text'
    app.run()
