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
            try:
                from win32api import GetSystemMetrics
                self.screen_resolution = (GetSystemMetrics(0), GetSystemMetrics(1))
            except:
                print('please install pypiwin32')
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

        self.left = (-self.aspect_ratio / 2, 0)
        self.right = (self.aspect_ratio / 2, 0)
        self.top = (0, .5)
        self.bottom = (0, .5)
        self.center = (0, 0)
        self.top_left = (-self.aspect_ratio / 2, .5)
        self.top_right = (self.aspect_ratio / 2, .5)
        self.bottom_left = (-self.aspect_ratio / 2, -.5)
        self.bottom_right = (self.aspect_ratio / 2, -.5)

        self.fullscreen = False
        self.borderless = True
        self.cursor = True
        self.fps_counter = False
        self.vsync = True


    def make_exit_button(self):     # called by main after setting up camera
        from pandaeditor.internal_prefabs.button import Button
        from pandaeditor import scene
        self.exit_button = Button()
        self.exit_button.is_editor = False
        self.exit_button.parent = scene.ui
        self.exit_button.name = 'exit_button_entity'
        self.exit_button.origin = (.5, .5)
        self.exit_button.position = self.top_right
        self.exit_button.scale = (.025, .025)
        self.exit_button.color = color.red
        self.exit_button.text = 'X'
        self.exit_button.add_script('exit_button')
        self.exit_button.enabled = True


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
            self.aspect_ratio = self.size[0] / self.size[1]
            if hasattr(camera, 'perspective_lens'):
                camera.perspective_lens.set_aspect_ratio(self.aspect_ratio)
                camera.ui_lens.set_film_size(camera.ui_size * .5 * self.aspect_ratio, camera.ui_size * .5)
            else:
                print('no camera (yet)')
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

        # if name == 'exit_button':
        #     if not hasattr(self, 'exit_button_entity'):
        #         self.make_exit_button()
        #     self.exit_button_entity.enabled = value

        # if name == 'borderless':
        #     self.set_undecorated(value)
        #     base.win.request_properties(self)
            # base.open_main_window(props=self)
            # self.load_defaults()


sys.modules[__name__] = Window()

if __name__ == '__main__':
    from pandaeditor import *
    app = PandaEditor()
    app.run()
