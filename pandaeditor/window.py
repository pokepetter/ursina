import sys
import os
from panda3d.core import WindowProperties
from panda3d.core import loadPrcFileData
from pandaeditor.entity import Entity
from pandaeditor import color
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


    def load_defaults(self):
        self.title = 'pandaeditor'

        if os.name == 'nt':
            from win32api import GetSystemMetrics
            self.screen_resolution = (GetSystemMetrics(0), GetSystemMetrics(1))
        elif os.name == 'posix':
            import subprocess
            output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]
            # TODO: test this in ubuntu

        self.fullscreen_size = (self.screen_resolution[0], self.screen_resolution[1])
        self.windowed_size = (self.fullscreen_size[0] / 1.25, self.fullscreen_size[1] / 1.25)
        # self.windowed_size = (self.fullscreen_size[0] / 2, self.fullscreen_size[1] / 1)
        self.size = self.windowed_size
        self.position = (
            int((self.screen_resolution[0] - self.size[0]) / 2),
            int((self.screen_resolution[1] - self.size[1]) / 2)
            )
        # self.position = (int(self.screen_resolution[0] / 2), 0)

        self.borderless = True
        self.fullscreen = False
        self.cursor = True
        self.fps_counter = False
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


    def make_exit_button(self):
        from pandaeditor.internal_prefabs.button import Button
        from pandaeditor import scene
        self.exit_button = Button()
        self.exit_button.is_editor = False
        self.exit_button.parent = scene.ui
        self.exit_button.name = 'exit_button button'
        self.exit_button.position = (.5, .5)
        self.exit_button.position = self.top_right
        self.exit_button.scale = (.025, .025)
        self.exit_button.color = color.red
        self.exit_button.text = 'X'
        self.exit_button.text_entity.x = 0
        self.exit_button.add_script('exit_button')


    def __setattr__(self, name, value):
        if not application.base:
            return
        try:
            super().__setattr__(name, value)
        except:
            pass
        if name == 'size':
            self.set_size(int(value[0]), int(value[1]))
            application.base.win.request_properties(self)
            object.__setattr__(self, name, value)

        if name == 'position':
            self.set_origin((value[0], value[1]))
            application.base.win.request_properties(self)
            object.__setattr__(self, name, value)

        if name == 'fullscreen':
            if value == True:
                self.size = self.fullscreen_size
            else:
                self.size = self.windowed_size
            object.__setattr__(self, name, value)

        if name == 'color':
            application.base.camNode.get_display_region(0).get_window().set_clear_color(value)

        if name == 'fps_counter':
            application.base.set_frame_rate_meter(value)

        if name == 'exit_button':
            try:
                self.exit_button.enabled = value
            except:
                self.make_exit_button()

        # if name == 'title':
        #     self.title = value

sys.modules[__name__] = Window()
