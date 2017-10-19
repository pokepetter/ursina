import sys
sys.path.append("..")
from pandaeditor import *

class Scrollable():

    def __init__(self):
        self.entity = None
        self.target = None

        self.max = .4
        self.min = -.4
        self.scroll_speed = .1


    def input(self, key):
        if not self.target:
            self.target = self.entity

        if self.entity.hovered:
            if key == 'scroll up':
                self.target.y -= self.scroll_speed
            if key == 'scroll down':
                self.target.y += self.scroll_speed

            self.target.y = max(min(self.target.y, self.max), self.min)
