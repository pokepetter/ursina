import sys
import time
sys.path.append("..")
from pandaeditor import *
from panda3d.core import TransparencyAttrib

from os import path
from panda3d.core import Filename
from panda3d.core import TextNode

class Text(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'text'
        self.character_spacing = .5
        self.line_height = 1
        self.character_limit = 50
        self.size = 1
        self.characters = list()
        self.scale *= 0.25
        self.origin = (0, 0)

        self.text_node = TextNode('node name')
        self.text_node.setText("Every day in every way I'm getting better and better.")
        self.text_node.setTextColor(color.text)
        self.text_node.setAlign(TextNode.ACenter)
        textNodePath = self.attachNewNode(self.text_node)
        textNodePath.setScale(1)
        self.setColorScaleOff()

        # temp
        # self.text_node.setFrameColor(1, 1, 1, 1)
        # self.text_node.setFrameAsMargin(0.5, 0.5, 0.5, 0.5)


        self.color = color.panda_text
        textNodePath.setLightOff()
        textNodePath.setBin("fixed", 0)

        # align = 0: top, 1: center, 2:bottom
        # bounds = self.getTightBounds()
        # z = 1 - bounds[1][2]
        # z = -(bounds[1] + bounds[0])[2] * .5
        # z = -bounds[0][2] -1

        z = -.3
        textNodePath.setZ(z)


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
            self.text_node.setText(value)

        if name == 'origin':
            object.__setattr__(self, name, value)
            try:
                self.set_origin(self.origin)
            except:
                pass
        #     self.update_text()
        if name == 'size':
            object.__setattr__(self, name, value)
            self.update_text()

        if name == 'color':
            object.__setattr__(self, name, value)
            try:
                self.text_node.setTextColor(value)
            except:
                pass

        if name == 'font':
            try:
                font_file = loader.loadFont(value)
                self.text_node.setFont(font_file)
            except:
                print('no font called:', value)
