from pandaeditor import *

class Quad(Entity):
    def __init__(self):
        super().__init__()
        self.model = 'quad'

class Circle(Entity):
    def __init__(self, segments=16):
        super().__init__()
        self.model = 'circle16'
        #gengerate circle16

class Cube(Entity):
    def __init__(self):
        super().__init__()
        self.model = 'cube'
