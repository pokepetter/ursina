import sys
import os
from panda3d.core import WindowProperties
from panda3d.core import loadPrcFileData
from panda3d.core import Vec2
from ursina.entity import Entity
from ursina import color
from ursina import application
try:
    from screeninfo import get_monitors
except:
    pass

class Window(WindowProperties):

    def __init__(self):
        super().__init__()
        loadPrcFileData('', 'window-title ursina')
        loadPrcFileData('', 'undecorated True')
        loadPrcFileData('', 'sync-video True')
        loadPrcFileData('', 'notify-level-util error')
        # loadPrcFileData("", "old-alpha-blend True")
        # loadPrcFileData('', 'notify-level-glgsg debug')
        # loadPrcFileData('', 'want-pstats True')
        self.setForeground(True)


    def load_defaults(self):
        self.title = os.path.basename(os.path.dirname(application.asset_folder))
        try:
            self.screen_resolution = (get_monitors()[0].width, get_monitors()[0].height)
        except:
            print('using default sceen resolution.', 'OS:', os.name)
            self.screen_resolution = (1366, 768)


        self.fullscreen_size = (self.screen_resolution[0]+1, (self.screen_resolution[0]+1) * .5625)
        self.windowed_size = (self.fullscreen_size[0] / 1.25, self.fullscreen_size[0] / 1.25 * .5625)
        self.size = self.windowed_size

        self.top = (0, .5)
        self.bottom = (0, .5)
        self.center = (0, 0)

        self.fullscreen = False
        self.borderless = True
        self.cursor = True
        self.fps_counter = True
        self.vsync = True


    @property
    def left(self):
        return (-self.aspect_ratio / 2, 0)
    @property
    def right(self):
        return (self.aspect_ratio / 2, 0)
    @property
    def top_left(self):
        return (-self.aspect_ratio / 2, .5)
    @property
    def top_right(self):
        return (self.aspect_ratio / 2, .5)
    @property
    def bottom_left(self):
        return (-self.aspect_ratio / 2, -.5)
    @property
    def bottom_right(self):
        return (self.aspect_ratio / 2, -.5)


    def center_on_screen(self):
        self.position = (
            int((self.screen_resolution[0] - self.size[0]) / 2),
            int((self.screen_resolution[1] - self.size[1]) / 2)
            )

    def make_exit_button(self):     # called by main after setting up camera
        from ursina.internal_prefabs.exit_button import ExitButton
        from ursina import scene
        self.exit_button = ExitButton()

    @property
    def size(self):
        return Vec2(self.get_size()[0], self.get_size()[1])

    @size.setter
    def size(self, value):
        self.set_size(int(value[0]), int(value[1]))
        self.aspect_ratio = value[0] / value[1]
        # base.camera.set_aspect_ratio(self.aspect_ratio)
        # camera.aspect_ratio = self.aspect_ratio
        # ui.lens.setFilmSize(100 * self.aspect_ratio, 100)
        base.win.requestProperties(self)

    # @property
    # def borderless(self):
    #     # return self._borderless
    #     return self.getUndecorated()
    #
    # @borderless.setter
    # def borderless(self, value):
    #     self.setUndecorated(value)
    #     application.base.win.request_properties(self)
    #     # base.openMainWindow(props=self)

    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except:
            pass

        if name == 'position':
            self.set_origin((value[0], value[1]))
            application.base.win.request_properties(self)
            object.__setattr__(self, name, value)

        if name == 'fullscreen':
            if value == True:
                self.size = self.fullscreen_size
            else:
                self.size = self.windowed_size

            self.center_on_screen()
            object.__setattr__(self, name, value)
            return

        if name == 'color':
            application.base.camNode.get_display_region(0).get_window().set_clear_color(value)

        if name == 'fps_counter':
            application.base.set_frame_rate_meter(value)

        if name == 'vsync':
            if value == True:
                loadPrcFileData('', 'sync-video True')
            else:
                loadPrcFileData('', 'sync-video False')
                print('set vsync to false')
            object.__setattr__(self, name, value)
            application.base.win.request_properties(self)


sys.modules[__name__] = Window()

if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    # window.size = (1024, 1024)

    # props = WindowProperties()
    # props.setSize(1024, 1024)
    # base.win.requestProperties(props)

    Entity(model='cube')
    # Button(text='test\ntest')
    app.run()
