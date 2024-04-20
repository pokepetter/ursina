import sys
import os
from panda3d.core import WindowProperties
from panda3d.core import loadPrcFileData
from ursina.vec2 import Vec2
from ursina import color, application
from ursina.scene import instance as scene    # for toggling collider visibility
from ursina.string_utilities import print_info, print_warning
from screeninfo import get_monitors


class Window(WindowProperties):

    def ready(self, title, icon, borderless, fullscreen, size, forced_aspect_ratio, position, vsync, editor_ui_enabled, window_type, render_mode):
        loadPrcFileData('', 'window-title ursina')
        loadPrcFileData('', 'notify-level-util error')
        loadPrcFileData('', 'textures-auto-power-2 #t')
        loadPrcFileData('', 'load-file-type p3assimp')
        # loadPrcFileData('', 'allow-portal-cull #t')
        # loadPrcFileData("", "framebuffer-multisample 1")
        # loadPrcFileData('', 'multisamples 2')
        # loadPrcFileData('', 'textures-power-2 none')
        # loadPrcFileData('', 'threading-model Cull/Draw')
        loadPrcFileData('', 'coordinate-system y-up-left')
        # fallback to one of these if opengl is not supported
        loadPrcFileData('', 'aux-display pandadx9')
        loadPrcFileData('', 'aux-display pandadx8')
        loadPrcFileData('', 'aux-display tinydisplay')

        loadPrcFileData('', f'undecorated {borderless}')
        self.title = title
        self.icon = icon

        self.monitors = []
        self.main_monitor = None
        self.monitor_index = 0
        try:
            self.monitors = get_monitors()
            if self.monitors:
                self.main_monitor = next((e for e in self.monitors if e.is_primary), self.monitors[0])
                if self.main_monitor.is_primary:
                    print_info(f'Using primary monitor: {self.main_monitor}')
                else:
                    print_info('No primary monitor found, using first monitor instead')
                self.monitor_index = self.monitors.index(self.main_monitor)
        except:
            print_warning('No monitors found')

        if not size:
            if self.main_monitor:
                self.fullscreen_size = Vec2(self.main_monitor.width, self.main_monitor.height)
                self.windowed_size = self.fullscreen_size / 1.25
            else:
                self.fullscreen_size = Vec2(1280,720)
                self.windowed_size = self.fullscreen_size / 1.25
        else:
            self.fullscreen_size = size
            self.windowed_size = size

        if not fullscreen:
            if forced_aspect_ratio is None:
                loadPrcFileData('', f'win-size {self.windowed_size[0]} {self.windowed_size[1]}')
            else:
                loadPrcFileData('', f'win-size {self.windowed_size[1] * forced_aspect_ratio} {self.windowed_size[1]}')
        else:
            loadPrcFileData('', f'win-size {self.fullscreen_size[0]} {self.fullscreen_size[1]}')

        self.windowed_position = None   # gets set when entering fullscreen so position will be correct when going back to windowed mode
        self.show_ursina_splash = False

        self.top = Vec2(0, .5)
        self.bottom = Vec2(0, -.5)
        self.center = Vec2(0, 0)


    def apply_settings(self):
        self.forced_aspect_ratio = None # example: window.forced_aspect_ratio = 16/9
        self.always_on_top = False

        self.vsync = True   # can't be set during play
        # self.borderless = borderless

        # if size:
        #     self.windowed_size = size
        # self.size = self.windowed_size

        # if fullscreen:
        #     self.fullscreen = fullscreen
        # self._fullscreen = not application.development_mode
        self.center_on_screen()



        self.color = color.dark_gray
        self.render_modes = ('default', 'wireframe', 'colliders', 'normals')
        self.render_mode = 'default'
        self.editor_ui = None
        if application.window_type != 'none':
            base.accept('aspectRatioChanged', self.update_aspect_ratio)
            if self.always_on_top:
                self.setZOrder(WindowProperties.Z_top)



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
        if application.window_type == 'none' or not self.main_monitor:
            return
        x = self.main_monitor.x + ((self.main_monitor.width - self.size[0]) / 2)
        y = self.main_monitor.y + ((self.main_monitor.height - self.size[1]) / 2)
        self.position = Vec2(x,y)


    def make_editor_gui(self):     # called by main after setting up camera and application.development_mode
        from ursina import camera, Entity, Text, Button, ButtonList, Func, Tooltip, held_keys, mouse
        import time

        self.editor_ui = Entity(parent=camera.ui, eternal=True, enabled=bool(application.development_mode))

        def window_input(key):
            if key == 'f12':
                self.editor_ui.enabled = not self.editor_ui.enabled

            elif key == 'f11':
                self.fullscreen = not self.fullscreen

            elif key == 'f10':
                if held_keys['shift']:
                    self.render_mode = 'default'
                else:
                    i = self.render_modes.index(self.render_mode) + 1
                    if i >= len(self.render_modes):
                        i = 0

                    self.render_mode = self.render_modes[i]
        self.input_entity = Entity(name = 'window.input_entity', input=window_input)

        self.exit_button = Button(parent=self.editor_ui, text='x', eternal=True, ignore_paused=True, origin=(.5, .5), enabled=self.borderless,
            position=self.top_right, z=-999, scale=(.05, .025), color=color.red.tint(-.2), on_click=application.quit, name='exit_button')

        def _exit_button_input(key):
            if held_keys['shift'] and key == 'q' and not mouse.right:
                self.exit_button.on_click()
        self.exit_button.input = _exit_button_input

        self.fps_counter = Text(parent=self.editor_ui, eternal=True, text='60', ignore=False, i=0, ignore_paused=True,
            position=((.5*self.aspect_ratio)-self.exit_button.scale_x, .47+(.02*(not self.exit_button.enabled)), -999))

        def _fps_counter_update():
            if self.fps_counter.i > 60:
                self.fps_counter.text = str(int(1//time.dt_unscaled))
                self.fps_counter.i = 0
            self.fps_counter.i += 1
        self.fps_counter.update = _fps_counter_update

        self.entity_counter = Text(parent=self.editor_ui, eternal=True, origin=(-.5,.5), text='00', ignore=False, t=0,
            position=((.5*self.aspect_ratio)-self.exit_button.scale_x, .425+(.02*(not self.exit_button.enabled)), -999))
        self.entity_counter.text_entity = Text(parent=self.entity_counter, text='entities:', origin=(-.5,-.75), scale=.4, add_to_scene_entities=False, eternal=True)
        def _entity_counter_update():
            if self.entity_counter.t > 1:
                self.entity_counter.text = str(max(0, len([e for e in scene.entities if e.model and e.enabled])-5))
                self.entity_counter.i = 0
            self.entity_counter.t += time.dt
        self.entity_counter.update = _entity_counter_update

        self.collider_counter = Text(parent=self.editor_ui, eternal=True, origin=(-.5,.5), text='00', ignore=False, t=.1,
            position=((.5*self.aspect_ratio)-self.exit_button.scale_x, .38+(.02*(not self.exit_button.enabled)), -999))
        self.collider_counter.text_entity = Text(parent=self.collider_counter, text='colliders:', origin=(-.5,-.75), scale=.4, add_to_scene_entities=False, eternal=True)
        def _collider_counter_update():
            if self.collider_counter.t > 1:
                self.collider_counter.text = str(max(0, len([e for e in scene.entities if e.collider and e.enabled])-4))
                self.collider_counter.i = 0
            self.collider_counter.t += time.dt
        self.collider_counter.update = _collider_counter_update


        import webbrowser
        self.cog_menu = ButtonList({
            # 'Build' : Func(print, ' '),
            'API Reference' : Func(webbrowser.open, 'https://www.ursinaengine.org/api_reference.html'),
            # 'Asset Store' : Func(webbrowser.open, 'https://itch.io/tools/tag-ursina'),
            'ursfx (Sound Effect Maker)' : lambda: exec('from ursina.prefabs import ursfx; ursfx.open_gui()'),
            # 'Open Scene Editor' : Func(print, ' '),
            'Change Render Mode <gray>[F10]<default>' : self.next_render_mode,
            'Reset Render Mode <gray>[Shift+F10]<default>' : Func(setattr, self, 'render_mode', 'default'),
            'Toggle Hotreloading <gray>[F9]<default>' : application.hot_reloader.toggle_hotreloading,
            'Reload Shaders <gray>[F7]<default>' : application.hot_reloader.reload_shaders,
            'Reload Models <gray>[F7]<default>' : application.hot_reloader.reload_models,
            'Reload Textures <gray>[F6]<default>' : application.hot_reloader.reload_textures,
            'Reload Code <gray>[F5]<default>' : application.hot_reloader.reload_code,
        },
            width=.4, scale=.75, x=(.5*self.aspect_ratio)-(.4*.75), enabled=False, eternal=True, name='cog_menu', z=-10, color=color.black90, ignore_paused=True,
        )
        self.cog_menu.on_click = self.cog_menu.disable
        # print(self.cog_menu.scale_y)
        # self.cog_menu.scale *= .75
        self.cog_menu.highlight.color = color.azure
        self.cog_button = Button(parent=self.editor_ui, eternal=True, model='quad', texture='cog', scale=.015, origin=(1,-1), position=self.bottom_right, ignore_paused=True, name='cog_button')
        self.cog_menu.y = self.cog_button.y + (self.cog_menu.bg.scale_y * self.cog_menu.scale_y) + Text.size
        info_text ='''This menu is not enabled in builds. To see how the app will look like in builds, do Ursina(development_mode=False), which will disable all editor ui and start the app in fullscreen. To disable only this menu, do window.cog_menu.enabled = False'''
        self.cog_menu.info = Button(parent=self.cog_menu, model='circle', text='<gray>?', scale=.025, origin=(.5,-.5), tooltip=Tooltip(info_text, scale=.75, origin=(-.5,-.5), eternal=True), eternal=True, name='cog_menu_info')
        self.cog_menu.info.text_entity.scale *= .75
        def _toggle_cog_menu():
            self.cog_menu.enabled = not self.cog_menu.enabled
        self.cog_button.on_click = _toggle_cog_menu
        # print('-----------', time.time() - t) # 0.04


    def update_aspect_ratio(self):
        if hasattr(self, 'prev_size'):
            self.prev_aspect_ratio = self.prev_size[0] / self.prev_size[1]
        else:
            self.prev_aspect_ratio = self.aspect_ratio

        self.prev_size = self.size

        from ursina import camera, window
        value = [int(e) for e in base.win.getSize()]
        camera.set_shader_input('window_size', value)

        print_info('changed aspect ratio:', round(self.prev_aspect_ratio, 3), '->', round(self.aspect_ratio, 3))

        camera.ui_lens.set_film_size(camera.ui_size * .5 * self.aspect_ratio, camera.ui_size * .5)
        for e in [e for e in scene.entities if e.parent == camera.ui] + self.editor_ui.children:
            e.x /= self.prev_aspect_ratio / self.aspect_ratio

        if camera.orthographic:
            camera.orthographic_lens.set_film_size(camera.fov * window.aspect_ratio, camera.fov)
            base.cam.node().set_lens(camera.orthographic_lens)


    @property
    def position(self):
        if application.window_type == 'none':
            return Vec2(0,0)

        return Vec2(*self.getOrigin())

    @position.setter
    def position(self, value):
        if application.window_type == 'none':
            return
        print('set window position:', value)
        self.setOrigin(int(value[0]), int(value[1]))
        if application.base and hasattr(application.base.win, 'request_properties'):
            application.base.win.request_properties(self)


    @property
    def size(self):
        try:
            return Vec2(*base.win.getSize())
        except:
            return Vec2(1280,720)

    @size.setter
    def size(self, value):
        if application.window_type == 'none' or not value:
            return

        print('---------------set size to:', value)
        if hasattr(self, '_forced_aspect_ratio') and self.forced_aspect_ratio:
            value = (value[1] * self.forced_aspect_ratio, value[1])

        self.setSize(int(value[0]), int(value[1]))
        if application.base and hasattr(application.base.win, 'request_properties'):
            application.base.win.request_properties(self)
        try:
            from ursina import camera
            camera.set_shader_input('window_size', value)
        except:
            pass # not initialized yet


    @property
    def aspect_ratio(self):
        try:
            w, h = base.win.getSize()
            return w / h
        except:
            return 16/9

    @property
    def forced_aspect_ratio(self):
        return getattr(self, '_forced_aspect_ratio', None)

    @forced_aspect_ratio.setter
    def forced_aspect_ratio(self, value):
        self._forced_aspect_ratio = value
        if not value:
            return

        self.size = self.size


    @property
    def render_mode(self):
        return getattr(self, '_render_mode', None)

    @render_mode.setter
    def render_mode(self, value):
        self._render_mode = value
        # print('render mode:', value)
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

        elif value == 'colliders':
            self.original_colors = [e.color for e in scene.entities if hasattr(e, 'color')]
            for e in scene.entities:
                e.color = color.clear
                if e.collider:
                    # e.visible = False
                    e.collider.visible = True

        elif value == 'normals':
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
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        loadPrcFileData('', f'window-title {value}')


    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value
        self.setIconFilename(value)


    @property
    def borderless(self):
        return getattr(self, '_borderless', True)

    @borderless.setter
    def borderless(self, value):
        self._borderless = value
        if application.window_type == 'none':
            return

        self.setUndecorated(value)
        if hasattr(self, 'exit_button'):
            self.exit_button.enabled = not value

        if application.base and hasattr(application.base.win, 'request_properties'):
            application.base.win.request_properties(self)


    @property
    def fullscreen(self):
        return getattr(self, '_fullscreen', True)


    @fullscreen.setter
    def fullscreen(self, value):
        # print('----------------------', value, self._fullscreen)
        self._fullscreen = value
        if application.window_type == 'none':
            return

        print('set fullscreen to', value)
        if value:
            print(self.main_monitor)
            self.windowed_position = self.position
            self.windowed_size = self.size
            self.position = Vec2(self.main_monitor.x, self.main_monitor.y)
            self.size = Vec2(self.main_monitor.width, self.main_monitor.height)
        else:
            self.size = self.windowed_size
            if self.windowed_position is not None:
                self.position = self.windowed_position
            else:
                self.center_on_screen()

        # self.setFullscreen(value)
        base.win.request_properties(self)
        # except:
        #     print_warning('failed to set fullscreen', value)
        #     pass

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        if application.window_type == 'none':
            return

        base.camNode.get_display_region(0).get_window().set_clear_color(value)


    @property
    def vsync(self):
        return self._vsync

    @vsync.setter
    def vsync(self, value):
        self._vsync = value
        if not 'base' in sys.modules:     # set vsync/framerate before window opened
            if value == True or value == False:
                loadPrcFileData('', f'sync-video {value}')
            elif isinstance(value, int):
                loadPrcFileData('', 'clock-mode limited')
                loadPrcFileData('', f'clock-frame-rate {value}')
        else:
            from panda3d.core import ClockObject                      # set vsync/framerate in runtime
            if value == True:
                globalClock.setMode(ClockObject.MNormal)
            elif value == False:
                print_warning('error: disabling vsync during runtime is not yet implemented')

            elif isinstance(value, (int, float, complex)):
                globalClock.setMode(ClockObject.MLimited)
                globalClock.setFrameRate(int(value))


instance = Window()


if __name__ == '__main__':
    from ursina import *
    # application.development_mode = False
    # app = Ursina(borderless=True, forced_aspect_ratio=16/9)
    app = Ursina(
        title='Ursina',
        # borderless=False,
        # borderless=True,
        # fullscreen=True,
        # show_ursina_splash=True,
        # development_mode=False,
        # vsync = True
        )
    button_list = ButtonList(
        {
        'widow.position = Vec2(0,0)': Func(setattr, window, 'position', Vec2(0,0)),
        'widow.size = Vec2(512,512)': Func(setattr, window, 'size', Vec2(512,512)),
        'widow.center_on_screen()': window.center_on_screen,

        'widow.borderless = True': Func(setattr, window, 'borderless', True),
        'widow.borderless = False': Func(setattr, window, 'borderless', False),

        'widow.fullscreen = True': Func(setattr, window, 'fullscreen', True),
        'widow.fullscreen = False': Func(setattr, window, 'fullscreen', False),

        'widow.vsync = True': Func(setattr, window, 'vsync', True),
        'widow.vsync = False': Func(setattr, window, 'vsync', False),


        'application.base.win.request_properties(self)': Func(application.base.win.request_properties, window),

        }, y=0
    )
    startup_value = Text(y=.5,x=-.5)
    startup_value.text = f'''
        position: {window.position}
        size: {window.size}
        aspect_ratio: {window.aspect_ratio}
        window.main_monitor.width: {window.main_monitor.width}
        window.main_monitor.height: {window.main_monitor.height}

    '''

    position_text = Text(y=.5,)

    # def update():
    #     position_text.text = f'''
    #         position: {window.position}
    #         size: {window.size}
    #         aspect_ratio: {window.aspect_ratio}
    #         window.main_monitor.width: {window.main_monitor.width}
    #         window.main_monitor.height: {window.main_monitor.height}
    #
    #     '''

    def input(key):
        if key == 'space':
            # x = window.main_monitor.x + ((window.main_monitor.width - window.size[0]) / 2)
            # y = window.main_monitor.y + ((window.main_monitor.height - window.size[1]) / 2)
            # window.position = Vec2(x,y)
            window.center_on_screen()

    # window.borderless = False
    # window.fullscreen = True

    # window.size = window.size - Vec2(1,1)
    # window.monitor_index = 0
    # window.center_on_screen()
    # print('------------', window.monitors)
    # time.sleep(2)
    # window.forced_aspect_ratio = 1
    # window.vsync = 10
    # window.title = 'ursina'
    # window.borderless = False
    # window.fullscreen = False
    # window.fps_counter.enabled = False
    # window.cog_button.enabled = False
    # window.position =(0,837)

    # camera.orthographic = True
    # camera.fov = 2
    # Text(text='adoij', x=.1)
    # def input(key):
    #     if key == 'space':
    #         window.center_on_screen()

    # Entity(model='cube', color=color.green, collider='box', texture='shore')
    app.run()
