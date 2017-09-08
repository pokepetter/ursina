import sys
from panda3d.core import WindowProperties
import scene
from panda3d.core import loadPrcFileData

class Window(WindowProperties):

    def __init__(self):
        super().__init__()
        loadPrcFileData('', 'window-title pandaeditor')
        loadPrcFileData('', 'undecorated True')
        loadPrcFileData('', 'sync-video True')
        loadPrcFileData('', 'show-frame-rate-meter True')

        self.setForeground(True)

        # self.fullscreen = False
        # self.set_cursor_hidden(True)
        # self.setCursorFilename(Filename.binaryFilename(cursorFile))

        # main.app.base.win.requestProperties(self)

    def load_defaults(self):
        self.title = 'pandaeditor'

        self.fullscreen_size = (1920, 1080)
        self.windowed_size = (1920 * .8, 1080 * .8)
        self.size = self.windowed_size

        self.borderless = True
        self.fullscreen = False

        self.cursor = True
        self.fps_counter = True
        self.vsync = True


    def __setattr__(self, name, value):
        if not scene.base:
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
            scene.base.win.requestProperties(self)
            object.__setattr__(self, name, value)

        if name == 'fullscreen':
            if value == True:
                self.size = self.fullscreen_size
            else:
                self.size = self.windowed_size
            object.__setattr__(self, name, value)


sys.modules[__name__] = Window()
