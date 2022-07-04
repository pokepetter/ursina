import time
import platform

from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from panda3d.core import KeyboardButton
from panda3d.core import ConfigVariableBool

from ursina import application
from ursina import input_handler
from ursina.window import instance as window
from ursina.scene import instance as scene
from ursina.camera import instance as camera
from ursina.mouse import instance as mouse
from ursina.string_utilities import print_info


import __main__
time.dt = 0


class Ursina(ShowBase):

    def __init__(self, **kwargs): # optional arguments: title, fullscreen, size, forced_aspect_ratio, position, vsync, borderless, show_ursina_splash, render_mode, development_mode, editor_ui_enabled.
        for name in ('size', 'vsync', 'forced_aspect_ratio'):
            if name in kwargs and hasattr(window, name):
                setattr(window, name, kwargs[name])

        if 'development_mode' in kwargs:
            application.development_mode = kwargs['development_mode']

        super().__init__()
        application.base = base

        try:
            import gltf
            gltf.patch_loader(self.loader)
        except:
            pass

        window.late_init()
        for name in ('title', 'fullscreen', 'position', 'show_ursina_splash', 'borderless', 'render_mode'):
            if name in kwargs and hasattr(window, name):
                setattr(window, name, kwargs[name])

        # camera
        camera._cam = base.camera
        camera._cam.reparent_to(camera)
        camera.render = base.render
        camera.position = (0, 0, -20)
        scene.camera = camera
        camera.set_up()

        # input
        base.buttonThrowers[0].node().setButtonDownEvent('buttonDown')
        base.buttonThrowers[0].node().setButtonUpEvent('buttonUp')
        base.buttonThrowers[0].node().setButtonRepeatEvent('buttonHold')
        base.buttonThrowers[0].node().setKeystrokeEvent('keystroke')
        self._input_name_changes = {
            'mouse1' : 'left mouse down',
            'mouse1 up' : 'left mouse up',
            'mouse2' : 'middle mouse down',
            'mouse2 up' : 'middle mouse up',
            'mouse3' : 'right mouse down',
            'mouse3 up' : 'right mouse up',
            'wheel_up' : 'scroll up',
            'wheel_down' : 'scroll down',
            'arrow_left' : 'left arrow',
            'arrow_left up' : 'left arrow up',
            'arrow_up' : 'up arrow',
            'arrow_up up' : 'up arrow up',
            'arrow_down' : 'down arrow',
            'arrow_down up' : 'down arrow up',
            'arrow_right' : 'right arrow',
            'arrow_right up' : 'right arrow up',
            'lcontrol' : 'left control',
            'rcontrol' : 'right control',
            'lshift' : 'left shift',
            'rshift' : 'right shift',
            'lalt' : 'left alt',
            'ralt' : 'right alt',
            'lcontrol up' : 'left control up',
            'rcontrol up' : 'right control up',
            'lshift up' : 'left shift up',
            'rshift up' : 'right shift up',
            'lalt up' : 'left alt up',
            'ralt up' : 'right alt up',
            'control-mouse1' : 'left mouse down',
            'control-mouse2' : 'middle mouse down',
            'control-mouse3' : 'right mouse down',
            'shift-mouse1' : 'left mouse down',
            'shift-mouse2' : 'middle mouse down',
            'shift-mouse3' : 'right mouse down',
            'alt-mouse1' : 'left mouse down',
            'alt-mouse2' : 'middle mouse down',
            'alt-mouse3' : 'right mouse down',
            'page_down' : 'page down',
            'page_down up' : 'page down up',
            'page_up' : 'page up',
            'page_up up' : 'page up up',
            }
        self.accept('buttonDown', self.input)
        self.accept('buttonUp', self.input_up)
        self.accept('buttonHold', self.input_hold)
        self.accept('keystroke', self.keystroke)
        ConfigVariableBool('paste-emit-keystrokes', False)

        base.disableMouse()
        mouse._mouse_watcher = base.mouseWatcherNode
        mouse.enabled = True
        self.mouse = mouse

        from ursina import gamepad

        scene.set_up()
        self._update_task = taskMgr.add(self._update, "update")

        # try to load settings that need to be applied before entity creation
        application.load_settings()

        from ursina.prefabs.hot_reloader import HotReloader
        # make sure it's running from a file and not an interactive session.
        application.hot_reloader = HotReloader(__main__.__file__ if hasattr(__main__, '__file__') else 'None')

        window.make_editor_gui()
        if 'editor_ui_enabled' in kwargs:
            window.editor_ui.enabled = kwargs['editor_ui_enabled']


    def _update(self, task):
        # time between frames
        time.dt = globalClock.getDt() * application.time_scale

        mouse.update()

        if hasattr(__main__, 'update') and __main__.update and not application.paused:
            __main__.update()

        for seq in application.sequences:
            seq.update()

        for entity in scene.entities:
            if entity.enabled == False or entity.ignore:
                continue

            if application.paused and entity.ignore_paused == False:
                continue

            if hasattr(entity, 'update') and callable(entity.update):
                entity.update()


            if hasattr(entity, 'scripts'):
                for script in entity.scripts:
                    if script.enabled and hasattr(script, 'update') and callable(script.update):
                        script.update()


        return Task.cont



    def input_up(self, key):
        if key in  ('wheel_up', 'wheel_down'):
            return

        key += ' up'
        self.input(key)


    def input_hold(self, key):
        key = key.replace('control-', '')
        key = key.replace('shift-', '')
        key = key.replace('alt-', '')

        if key in self._input_name_changes:
            key = self._input_name_changes[key]

        key += ' hold'
        self.input(key)


    def input(self, key):
        key = key.replace('control-', '')
        key = key.replace('shift-', '')
        key = key.replace('alt-', '')

        if key in self._input_name_changes:
            key = self._input_name_changes[key]

        if key in input_handler.rebinds:
            key = input_handler.rebinds[key]

        try: input_handler.input(key)
        except: pass
        if not application.paused:
            if hasattr(__main__, 'input'):
                __main__.input(key)


        for entity in scene.entities:
            if entity.enabled == False or entity.ignore or entity.ignore_input:
                continue
            if application.paused and entity.ignore_paused == False:
                continue

            if hasattr(entity, 'input') and callable(entity.input):
                entity.input(key)

            if hasattr(entity, 'scripts'):
                for script in entity.scripts:
                    if script.enabled and hasattr(script, 'input') and callable(script.input):
                        script.input(key)


        try: mouse.input(key)
        except: pass


        if key == 'f12':
            window.editor_ui.enabled = not window.editor_ui.enabled

        if key == 'f11':
            window.fullscreen = not window.fullscreen

        if key == 'f10':
            i = window.render_modes.index(window.render_mode)
            i += 1
            if i >= len(window.render_modes):
                i = 0

            window.render_mode = window.render_modes[i]

        if key == 'f9':
            window.render_mode = 'default'


    def keystroke(self, key):
        key = str(KeyboardButton.asciiKey(key))

        if key == None:
            return
        if key == 'space':
            key = ' '
        if len(key) != 1:
            return

        if not application.paused:
            if hasattr(__main__, 'keystroke'):
                __main__.keystroke(key)

        for entity in scene.entities:
            if entity.enabled == False or entity.ignore or entity.ignore_input:
                continue
            if application.paused and entity.ignore_paused == False:
                continue

            if hasattr(entity, 'keystroke') and callable(entity.keystroke):
                entity.keystroke(key)

            if hasattr(entity, 'scripts'):
                for script in entity.scripts:
                    if script.enabled and hasattr(script, 'keystroke') and callable(script.keystroke):
                        script.keystroke(key)

    def step(self):     # use this control the update loop yourself. call app.step() in a while loop for example, instead of app.run()
        self.taskMgr.step()


    def run(self, info=True):
        if window.show_ursina_splash:
            from ursina.prefabs import ursina_splash

        application.load_settings()
        if info:
            print('screen resolution:', window.screen_resolution)
            print('os:', platform.system())
            print('development mode:', application.development_mode)
            print('application successfully started')

        super().run()


if __name__ == '__main__':
    app = Ursina()
    app.run()
