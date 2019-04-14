import sys
import os
from panda3d.core import WindowProperties
from panda3d.core import loadPrcFileData
from panda3d.core import Vec2
from ursina.entity import Entity
from ursina import color
from ursina import application
from ursina import scene    # for toggling collider visibility
from ursina.thirdparty.screeninfo import get_monitors


class Window(WindowProperties):

    def __init__(self):
        super().__init__()
        loadPrcFileData('', 'window-title ursina')
        loadPrcFileData('', 'undecorated True')
        loadPrcFileData('', 'sync-video True')
        loadPrcFileData('', 'notify-level-util error')
        # loadPrcFileData('', 'textures-power-2 pad')
        loadPrcFileData('', 'textures-auto-power-2 #t')
        # loadPrcFileData('', 'want-pstats True')
        self.setForeground(True)


    def late_init(self):
        self.title = os.path.basename(os.path.dirname(application.asset_folder))
        try:
            self.screen_resolution = (get_monitors()[0].width, get_monitors()[0].height)
        except:
            print('using default sceen resolution.', 'OS:', os.name)
            self.screen_resolution = (1366, 768)


        self.fullscreen_size = (self.screen_resolution[0]+1, (self.screen_resolution[0]+1) * .5625)
        self.windowed_size = (self.fullscreen_size[0] / 1.25, self.fullscreen_size[0] / 1.25 * .5625)
        self.size = self.windowed_size
        self.position = (0,0)

        self.top = (0, .5)
        self.bottom = (0, .5)
        self.center = (0, 0)

        self.fullscreen = False
        self.borderless = True
        self.cursor = True
        self.vsync = True

        self.color = color.dark_gray
        self.display_modes = (
            'default',
            'wireframe',
            'colliders',
            'normals',
            'vertices',
            'textureless',
            'cubes'
            )
        self.display_mode = 'default'


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
        from ursina.prefabs.exit_button import ExitButton
        from ursina import scene
        self.exit_button = ExitButton()

        from ursina import Text
        import time
        self.fps_counter = Text(
            parent = scene.ui,
            eternal = True,
            position = (.5*self.aspect_ratio, .47),
            origin = (.8,.5),
            text = '60',
            # background = True,
            i = 0,
            )
        def update():
            if self.fps_counter.i > 60:
                self.fps_counter.text = str(int(1//time.dt))
                self.fps_counter.i = 0

            self.fps_counter.i += 1

        self.fps_counter.update = update

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

    @property
    def display_mode(self):
        return self._display_mode

    @display_mode.setter
    def display_mode(self, value):
        self._display_mode = value
        print('display mode:', value)
        # print_on_screen('display mode:', value)
        # if value == 'default':
        # disable wireframe mode
        base.wireframeOff()
        # disable collision display mode
        if hasattr(self, 'original_colors'):
            for i, e in enumerate([e for e in scene.entities if hasattr(e, 'color')]):
                e.color = self.original_colors[i]
                if e.collider:
                    e.collider.visible = False
        if hasattr(self, 'original_vert_colors'):
            for i, e in enumerate([e for e in scene.entities if hasattr(e, 'model') and e.model.colors]):
                e.model.colors = self.original_vert_colors[i]
                e.model.generate()


        if value == 'wireframe':
            base.wireframeOn()

        if value == 'colliders':
            self.original_colors = [e.color for e in scene.entities if hasattr(e, 'color')]
            for e in scene.entities:
                e.color = color.clear
                if e.collider:
                    e.collider.visible = True

        if value == 'normals':
            # todo: set shader instead
            # self.original_colors = [e.color for e in scene.entities if hasattr(e, 'color')]
            self.original_vert_colors = [e.model.colors for e in scene.entities if hasattr(e, 'model') and e.model != None]
            # for e in scene.entities:
            #     e.color = color.clear
            #     if hasattr(e, 'model'):
            for e in scene.entities:
                if hasattr(e, 'model') and e.model != None:
                    try:
                        e.model.colorize()
                    except:
                        pass

            # bake_vertex_shading(entity)



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
    window.title = 'Title'
    window.color = color.black  # sets clear color
    # window.size *= .5
    app.run()
