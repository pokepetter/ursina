import sys


class Scene(object):

    def __init__(self):
        self.app = None
        self.render = None
        self.camera = None
        self.ui = None
        self.entities = []


sys.modules[__name__] = Scene()
