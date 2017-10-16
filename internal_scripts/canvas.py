import sys
sys.path.append("..")
from pandaeditor import *

class Canvas():

    def __init__(self):
        self.is_editor = True
        self.target = None


    def start(self):
        print('start')
        self.original_parent = self.entity.parent
        self.entity.parent = scene.ui

    def stop(self):
        self.entity.parent = self.original_parent
        self.entity.position = (0,0,0)
