import sys
import os
from panda3d.core import WindowProperties
from panda3d.core import loadPrcFileData
from panda3d.core import Vec2
from ursina.entity import Entity
from ursina import color
from ursina import application
from ursina.scene import instance as scene    # for toggling collider visibility


class Window(WindowProperties):

    def __init__(self):
        super().__init__()
        loadPrcFileData('', 'window-title ursina')
        loadPrcFileData('', 'notify-level-util error')
        loadPrcFileData('', 'textures-auto-power-2 #t')
        loadPrcFileData('', 'load-file-type p3assimp')
        # loadPrcFileData('', 'allow-portal-cull #t')
        # loadPrcFileData("", "framebuffer-multisample 1")
        # loadPrcFileData('', 'multisamples 2')
        # loadPrcFileData('', 'textures-power-2 none')

        # loadPrcFileData('', 'cursor-filename mycursor.ico')
        # loadPrcFileData('', 'threading-model Cull/Draw')
        loadPrcFileData('', 'coordinate-system y-up-left')

        # fallback to one of these if opengl is not supported
        loadPrcFileData('', 'aux-display pandadx9')
        loadPrcFileData('', 'aux-display pandadx8')
        loadPrcFileData('', 'aux-display tinydisplay')

        self.setForeground(True)
        self.vsync = True   # can't be set during play
        self.show_ursina_splash = False

        self.title = application.asset_folder.name
        if os.name == 'nt':     # windows
            import ctypes
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            self.screen_resolution = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))

        else:
            try:
                from screeninfo import get_monitors
                self.screen_resolution = (get_monitors()[0].width, get_monitors()[0].height)
                print('OS:', os.name)
            except:
                print('using default sceen resolution.', 'OS:', os.name)
                self.screen_resolution = Vec2(1366, 768)

        print('screen resolution:', self.screen_resolution)
        self.fullscreen_size = Vec2(self.screen_resolution[0]+1, self.screen_resolution[1]+1)
        self.windowed_size = self.fullscreen_size / 1.25
        self.windowed_position = None   # gets set when entering fullscreen so position will be correct when going back to windowed mode
        self.size = self.windowed_size
        self.borderless = True

        self.top = Vec2(0, .5)
        self.bottom = Vec2(0, -.5)
        self.center = Vec2(0, 0)



    def late_init(self):
        self.center_on_screen()
        if not application.development_mode:
            self.fullscreen = True

        self.cursor = True
        self.color = color.dark_gray
        self.render_modes = ('default', 'wireframe', 'colliders', 'normals')
        self.render_mode = 'default'
        self.editor_ui = None

        from ursina import invoke
        invoke(base.accept, 'aspectRatioChanged', self.update_aspect_ratio, delay=1/60)

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
        print('size;', self.size)
        self.position = Vec2(
            int((self.screen_resolution[0] - self.size[0]) / 2),
            int((self.screen_resolution[1] - self.size[1]) / 2)
            )

    def make_editor_gui(self):     # called by main after setting up camera and application.development_mode
        from ursina import camera, Text, Button, ButtonList, Func, Tooltip
        import time

        self.editor_ui = Entity(parent=camera.ui, eternal=True, enabled=bool(application.development_mode))
        self.exit_button = Button(parent=self.editor_ui, eternal=True, ignore_paused=True, origin=(.5, .5),
            position=self.top_right, z=-999, scale=(.05, .025), color=color.red.tint(-.2), text='x', on_click=application.quit)
        self.exit_button.enabled = self.borderless


        def _exit_button_input(key):
            from ursina import held_keys, mouse
            if held_keys['shift'] and key == 'q' and not mouse.right:
                self.exit_button.on_click()
        self.exit_button.input = _exit_button_input

        self.fps_counter = Text(parent=self.editor_ui, eternal=True, position=(.5*self.aspect_ratio, .47, -999), origin=(.8,.5), text='60', ignore=False, i=0)

        def _fps_counter_update():
            if self.fps_counter.i > 60:
                self.fps_counter.text = str(int(1//time.dt))
                self.fps_counter.i = 0
            self.fps_counter.i += 1
        self.fps_counter.update = _fps_counter_update


        import webbrowser
        self.cog_menu = ButtonList({
            # 'Build' : Func(print, ' '),
            'API Reference' : Func(webbrowser.open, 'https://www.ursinaengine.org/cheat_sheet_dark.html'),
            'Asset Store' : Func(webbrowser.open, 'https://itch.io/tools/tag-ursina'),
            # 'Open Scene Editor' : Func(print, ' '),
            'Change Render Mode <gray>[F10]<default>' : self.next_render_mode,
            'Reset Render Mode <gray>[F9]<default>' : Func(setattr, self, 'render_mode', 'default'),
            'Reload Models <gray>[F7]<default>' : application.hot_reloader.reload_models,
            'Reload Textures <gray>[F6]<default>' : application.hot_reloader.reload_textures,
            'Reload Code <gray>[F5]<default>' : application.hot_reloader.reload_code,
        },
            width=.35,
            x=.62,
            enabled=False,
            eternal=True
        )
        self.cog_menu.on_click = Func(setattr, self.cog_menu, 'enabled', False)
        self.cog_menu.y = -.5 + self.cog_menu.scale_y
        self.cog_menu.scale *= .75
        self.cog_menu.text_entity.x += .025
        self.cog_menu.highlight.color = color.azure
        self.cog_button = Button(parent=self.editor_ui, eternal=True, model='circle', scale=.015, origin=(1,-1), position=self.bottom_right)
        info_text ='''This menu is not enabled in builds <gray>(unless you set application.development to be not False).'''
        self.cog_menu.info = Button(parent=self.cog_menu, model='quad', text='<gray>?', scale=.1, x=1, y=.01, origin=(.5,-.5), tooltip=Tooltip(info_text, scale=.75, origin=(-.5,-.5)))
        self.cog_menu.info.text_entity.scale *= .75
        def _toggle_cog_menu():
            self.cog_menu.enabled = not self.cog_menu.enabled
        self.cog_button.on_click = _toggle_cog_menu
        # print('-----------', time.time() - t) # 0.04


    def update_aspect_ratio(self):
        prev_aspect = self.aspect_ratio
        self.size = base.win.get_size()
        print('changed aspect ratio:', round(prev_aspect, 3), '->', round(self.aspect_ratio, 3))

        from ursina import camera, window, application
        camera.ui_lens.set_film_size(camera.ui_size * .5 * self.aspect_ratio, camera.ui_size * .5)
        for e in [e for e in scene.entities if e.parent == camera.ui] + self.editor_ui.children:
            e.x /= prev_aspect / self.aspect_ratio

        if camera.orthographic:
            camera.orthographic_lens.set_film_size(camera.fov * window.aspect_ratio, camera.fov)
            application.base.cam.node().set_lens(camera.orthographic_lens)


    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        # print('set window position:', value)
        self._position = value
        self.setOrigin(int(value[0]), int(value[1]))
        base.win.request_properties(self)


    @property
    def size(self):
        return Vec2(self.get_size()[0], self.get_size()[1])

    @size.setter
    def size(self, value):
        self.set_size(int(value[0]), int(value[1]))
        self.aspect_ratio = value[0] / value[1]
        from ursina import camera
        camera.set_shader_input('window_size', value)


    @property
    def render_mode(self):
        return self._render_mode

    @render_mode.setter
    def render_mode(self, value):
        self._render_mode = value
        print('render mode:', value)
        base.wireframeOff()

        # disable collision display mode
        if hasattr(self, 'original_colors'):
            for i, e in enumerate([e for e in scene.entities if hasattr(e, 'color')]):
                e.color = self.original_colors[i]
                if e.collider:
                    e.collider.visible = False

        for e in [e for e in scene.entities if e.model and e.alpha]:
            e.setShaderAuto()

        if value == 'wireframe':
            base.wireframeOn()

        if value == 'colliders':
            self.original_colors = [e.color for e in scene.entities if hasattr(e, 'color')]
            for e in scene.entities:
                e.color = color.clear
                if e.collider:
                    # e.visible = False
                    e.collider.visible = True

        if value == 'normals':
            from ursina.shaders import normals_shader
            for e in [e for e in scene.entities if e.model and e.alpha]:
                e.shader = normals_shader
                e.set_shader_input('transform_matrix', e.getNetTransform().getMat())


    def next_render_mode(self):
        i = self.render_modes.index(self.render_mode) + 1
        if i >= len(self.render_modes):
            i = 0

        self.render_mode = self.render_modes[i]


    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value
        self.setIconFilename(value)


    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except:
            pass

        if name == 'fullscreen':
            try:
                if value == True:
                    self.windowed_position = self.position
                    self.windowed_size = self.size
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
            if hasattr(self, 'exit_button'):
                self.exit_button.enabled = not value
            try:
                application.base.win.request_properties(self)
            except:
                pass
            object.__setattr__(self, name, value)


        if name == 'color':
            application.base.camNode.get_display_region(0).get_window().set_clear_color(value)

        if name == 'vsync':
            if value == True:
                loadPrcFileData('', 'sync-video True')
            else:
                loadPrcFileData('', 'sync-video False')
                print('set vsync to false')
            object.__setattr__(self, name, value)


instance = Window()


if __name__ == '__main__':
    from ursina import *
    # application.development_mode = False
    app = Ursina()

    window.title = 'Title'
    window.borderless = False
    # window.fullscreen = False
    window.fps_counter.enabled = False
    # window.exit_button.visible = False
    # window.cog_button.enabled = False
    camera.orthographic = True

    camera.fov = 2

    Entity(model='cube', color=color.green, collider='box', texture='shore')
    app.run()
