from pandaeditor import *

class Quad(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'quad'
        # super().__init__(**kwargs)
# def Quad(self, **kwargs):
#     e = Entity()

class Circle(Entity):
    def __init__(self, segments=16):
        super().__init__()
        self.model = 'circle_16'
        #gengerate circle16

class Cube(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'cube'


if __name__ == '__main__':
    app = PandaEditor()
    # c = Circle()
    e = Entity(model='quad')
    e.model = 'circle_16'
    # print('----', e.model)
    # # e.rotation_y = 90
    app.run()
