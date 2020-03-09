import sys
import os
from panda3d.core import WindowProperties
from panda3d.core import loadPrcFileData
from panda3d.core import Vec2
from screeninfo import get_monitors
from ursina.entity import Entity
from ursina import color
from ursina import application
from ursina import scene    # for toggling collider visibility


class Window(WindowProperties):

    def __init__(self):
        super().__init__()
        loadPrcFileData('', 'window-title ursina')
        loadPrcFileData('', 'notify-level-util error')
        loadPrcFileData('', 'textures-auto-power-2 #t')
        self.setForeground(True)
        self.vsync = True   # can't be set during play
        self.show_ursina_splash = False

        self.title = application.asset_folder.name
        try:
            self.screen_resolution = (get_monitors()[0].width, get_monitors()[0].height)
        except:
            print('using default sceen resolution.', 'OS:', os.name)
            self.screen_resolution = Vec2(1366, 768)

        self.fullscreen_size = Vec2(self.screen_resolution[0]+1, ((self.screen_resolution[0]) * .5625)+1)
        self.windowed_size = Vec2(self.fullscreen_size[0] / 1.25, self.fullscreen_size[0] / 1.25 * .5625)
        self.windowed_position = None   # gets set when entering fullscreen so position will be correct when going back to windowed mode
        self.size = self.windowed_size
        self.borderless = True


    def late_init(self):
        self.position = Vec2(0,0)
        self.top = Vec2(0, .5)
        self.bottom = Vec2(0, .5)
        self.center = Vec2(0, 0)
        self.fullscreen = False

        self.cursor = True
        self.vsync = True

        self.color = color.dark_gray
        self.display_modes = (
            'default',
            'wireframe',
            'colliders',
            'normals',
            )
        self.display_mode = 'default'


    @property
    def left(self):
        return Vec2(-self.aspect_ratio/2, 0)
    @property
    def right(self):
        return Vec2(self.aspect_ratio/2, 0)
    @property
    def top_left(self):
        return Vec2(-self.aspect_ratio/2, .5)
    @property
    def top_right(self):
        return Vec2(self.aspect_ratio/2, .5)
    @property
    def bottom_left(self):
        return Vec2(-self.aspect_ratio/2, -.5)
    @property
    def bottom_right(self):
        return Vec2(self.aspect_ratio/2, -.5)


    def center_on_screen(self):
        self.position = Vec2(
            int((self.screen_resolution[0] - self.size[0]) / 2),
            int((self.screen_resolution[1] - self.size[1]) / 2)
            )

    def make_exit_button(self):     # called by main after setting up camera
        from ursina.prefabs.exit_button import ExitButton
        self.exit_button = ExitButton()

        from ursina import Text
        import time
        self.fps_counter = Text(
            name = 'fps_counter',
            parent = scene.ui,
            eternal = True,
            position = (.5*self.aspect_ratio, .47, -999),
            origin = (.8,.5),
            text = '60',
            add_to_scene_entities = True,
            # background = True,
            i = 0,
            )
        def update():
            if self.fps_counter.i > 60:
                self.fps_counter.text = str(int(1//time.dt))
                self.fps_counter.i = 0

            self.fps_counter.i += 1

        self.fps_counter.update = update

        self.overlay = Entity(
            name = 'overlay',
            parent = scene.ui,
            model = 'quad',
            scale_x = self.aspect_ratio,
            color = color.clear,
            eternal = True,
            z = -99
            )

    @property
    def size(self):
        return Vec2(self.get_size()[0], self.get_size()[1])

    @size.setter
    def size(self, value):
        self.set_size(int(value[0]), int(value[1]))
        self.aspect_ratio = value[0] / value[1]
        base.win.requestProperties(self)

    @property
    def display_mode(self):
        return self._display_mode

    @display_mode.setter
    def display_mode(self, value):
        self._display_mode = value
        print('display mode:', value)
        base.wireframeOff()

        # disable collision display mode
        if hasattr(self, 'original_colors'):
            for i, e in enumerate([e for e in scene.entities if hasattr(e, 'color')]):
                e.color = self.original_colors[i]
                if e.collider:
                    e.collider.visible = False

        for e in [e for e in scene.entities if e.model and e.alpha]:
            e.shader = None

        if value == 'wireframe':
            base.wireframeOn()

        if value == 'colliders':
            self.original_colors = [e.color for e in scene.entities if hasattr(e, 'color')]
            for e in scene.entities:
                e.color = color.clear
                if e.collider:
                    e.collider.visible = True

        if value == 'normals':
            from ursina.shaders import normals_shader
            for e in [e for e in scene.entities if e.model and e.alpha]:
                e.shader = normals_shader
                e.set_shader_input('transform_matrix', e.getNetTransform().getMat())




    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except:
            pass

        if name == 'position':
            self.setOrigin(int(value[0]), int(value[1]))
            application.base.win.request_properties(self)
            object.__setattr__(self, name, value)

        if name == 'fullscreen':
            try:
                if value == True:
                    self.windowed_size = self.size
                    self.windowed_position = self.position
                    self.size = self.fullscreen_size
                    self.center_on_screen()
                else:
                    self.size = self.windowed_size
                    if self.windowed_position is not None:
                        self.position = self.windowed_position
                    else:
                        self.center_on_screen()

                object.__setattr__(self, name, value)
                return
            except:
                print('failed to set fullscreen', value)
                pass

        if name == 'borderless':
            self.setUndecorated(value)

        if name == 'color':
            application.base.camNode.get_display_region(0).get_window().set_clear_color(value)

        if name == 'vsync':
            if value == True:
                loadPrcFileData('', 'sync-video True')
            else:
                loadPrcFileData('', 'sync-video False')
                print('set vsync to false')
            object.__setattr__(self, name, value)


sys.modules[__name__] = Window()

if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    window.title = 'Title'
    window.borderless = False
    window.fullscreen = False
    window.exit_button.visible = False
    window.fps_counter.enabled = False

    app.run()
