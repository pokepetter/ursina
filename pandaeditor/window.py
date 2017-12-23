import sys
from panda3d.core import WindowProperties
from panda3d.core import loadPrcFileData
from pandaeditor.entity import Entity
from pandaeditor import application


class Window(WindowProperties):

    def __init__(self):
        super().__init__()
        loadPrcFileData('', 'window-title pandaeditor')
        loadPrcFileData('', 'undecorated True')
        loadPrcFileData('', 'sync-video True')
        loadPrcFileData('', 'win-size 1536 864')
        loadPrcFileData('', 'notify-level-util error')
        # loadPrcFileData('', 'want-pstats True')

        self.setForeground(True)
        # self.exit = load_prefab('button')
        # self.exit.is_editor = False
        # self.exit.parent = self
        # self.exit.name = 'toggle_button'
        # self.exit.origin = (.5, .5)
        # self.exit.position = window.top_right
        # self.exit.scale = (.06, .03)
        # self.exit.text = 'X'
        # self.exit.text_entity.x = 0


    def load_defaults(self):
        self.title = 'pandaeditor'

        self.fullscreen_size = (1921, 1081)
        self.windowed_size = (1920 / 1.25, 1080 / 1.25)
        self.size = self.windowed_size

        self.borderless = True
        self.fullscreen = False

        self.cursor = True
        self.fps_counter = False
        # self.exit_button = True
        self.vsync = True


        self.aspect_ratio = self.size[0] / self.size[1]
        self.left = (-self.aspect_ratio / 2, 0)
        self.right = (self.aspect_ratio / 2, 0)
        self.top = (0, .5)
        self.bottom = (0, .5)
        self.center = (0, 0)
        self.top_left = (-self.aspect_ratio / 2, .5)
        self.top_right = (self.aspect_ratio / 2, .5)
        self.bottom_left = (-self.aspect_ratio / 2, -.5)
        self.bottom_right = (self.aspect_ratio / 2, -.5)


    def __setattr__(self, name, value):
        if not application.base:
            return
        try:
            super().__setattr__(name, value)
        except:
            pass
        if name == 'size':
            self.setSize(int(value[0]), int(value[1]))
            self.setOrigin(
                int((1920 - value[0]) / 2),
                int((1080 - value[1]) / 2))

            application.base.win.requestProperties(self)
            object.__setattr__(self, name, value)

        if name == 'fullscreen':
            if value == True:
                self.size = self.fullscreen_size
            else:
                self.size = self.windowed_size
            object.__setattr__(self, name, value)

        if name == 'color':
            application.base.camNode.getDisplayRegion(0).getWindow().setClearColor(value)

        if name == 'fps_counter':
            application.base.setFrameRateMeter(value)

        if name == 'exit_button':
            self.exit.enabled = value

        # if name == 'title':
        #     self.title = value


sys.modules[__name__] = Window()
