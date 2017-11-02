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
        # self.model = 'quad'
        # self.color = color.clear
        self.character_spacing = .5
        self.line_height = 1
        self.character_limit = 50
        # self.text = ''
        self.size = 1
        self.characters = list()
        self.scale *= 0.255
        self.origin = (0, 0)
        self.x = 0

        self.text_node = TextNode('node name')
        self.text_node.setText("Every day in every way I'm getting better and better.")
        self.text_node.setTextColor(color.white)
        self.text_node.setTextColor(1,1,1,1)
        self.text_node.setAlign(TextNode.ABoxedCenter)
        textNodePath = self.attachNewNode(self.text_node)
        textNodePath.setScale(1)
        textNodePath.setPos(0, -.1, 0)


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
