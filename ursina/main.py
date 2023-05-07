import time
import platform

from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
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
keyboard_keys = '1234567890qwertyuiopasdfghjklzxcvbnm'

def singleton(cls, **kwargs):
    instances = {}
    def getinstance(**kwargs):
        if cls not in instances:
            instances[cls] = cls(**kwargs)
        return instances[cls]
    return getinstance

@singleton
class Ursina(ShowBase):
    def __init__(self, **kwargs): # optional arguments: title, fullscreen, size, forced_aspect_ratio, position, vsync, borderless, show_ursina_splash, render_mode, development_mode, editor_ui_enabled, window_type='onscreen'/'offscreen'/'none'.
        """The main class of Ursina. This class is a singleton, so you can only have one instance of it.

        Keyword Args (optional):
            title (str): The title of the window.\n
            fullscreen (bool): Whether the window should be fullscreen or not.\n
            size (tuple(int, int)): The size of the window.\n
            forced_aspect_ratio (bool): Whether the window should have a forced aspect ratio or not.\n
            position (tuple(int, int)): The position of the window.\n
            vsync (bool): Whether the window should have vsync enabled or not.\n
            borderless (bool): Whether the window should be borderless or not.\n
            show_ursina_splash (bool): Whether the Ursina splash should be shown or not.\n
            render_mode (str): The render mode of the window.\n
            development_mode (bool): Whether the development mode should be enabled or not.\n
            editor_ui_enabled (bool): Whether the editor UI should be enabled or not.\n
            window_type (str): The type of the window. Can be 'onscreen', 'offscreen' or 'none'.\n
        """
        for name in ('title', 'size', 'vsync', 'forced_aspect_ratio'):
            if name in kwargs and hasattr(window, name):
                setattr(window, name, kwargs[name])

        if 'development_mode' in kwargs:
            application.development_mode = kwargs['development_mode']

        application.window_type = 'onscreen'
        if 'window_type' in kwargs:
            application.window_type = kwargs['window_type']
        # application.window_type = window_type

        application.base = self
        super().__init__(windowType=application.window_type)

        try:
            import gltf
            gltf.patch_loader(self.loader)
        except:
            pass

        if 'gltf_no_srgb' in kwargs:
            application.gltf_no_srgb = kwargs['gltf_no_srgb']

        window.late_init()
        for name in ('fullscreen', 'position', 'show_ursina_splash', 'borderless', 'render_mode'):
            if name in kwargs and hasattr(window, name):
                setattr(window, name, kwargs[name])

        # camera
        if application.window_type != 'none':
            camera._cam = self.camera
            camera._cam.reparent_to(camera)
            camera.render = self.render
            camera.position = (0, 0, -20)
            scene.camera = camera
            camera.set_up()

        # input
        if application.window_type == 'onscreen':
            self.buttonThrowers[0].node().setButtonDownEvent('buttonDown')
            self.buttonThrowers[0].node().setButtonUpEvent('buttonUp')
            self.buttonThrowers[0].node().setButtonRepeatEvent('buttonHold')
            self.buttonThrowers[0].node().setKeystrokeEvent('keystroke')
        self._input_name_changes = {
            'mouse1' : 'left mouse down', 'mouse1 up' : 'left mouse up', 'mouse2' : 'middle mouse down', 'mouse2 up' : 'middle mouse up', 'mouse3' : 'right mouse down', 'mouse3 up' : 'right mouse up',
            'wheel_up' : 'scroll up', 'wheel_down' : 'scroll down',
            'arrow_left' : 'left arrow', 'arrow_left up' : 'left arrow up', 'arrow_up' : 'up arrow', 'arrow_up up' : 'up arrow up', 'arrow_down' : 'down arrow', 'arrow_down up' : 'down arrow up', 'arrow_right' : 'right arrow', 'arrow_right up' : 'right arrow up',
            'lcontrol' : 'left control', 'rcontrol' : 'right control', 'lshift' : 'left shift', 'rshift' : 'right shift', 'lalt' : 'left alt', 'ralt' : 'right alt',
            'lcontrol up' : 'left control up', 'rcontrol up' : 'right control up', 'lshift up' : 'left shift up', 'rshift up' : 'right shift up', 'lalt up' : 'left alt up', 'ralt up' : 'right alt up',
            'control-mouse1' : 'left mouse down', 'control-mouse2' : 'middle mouse down', 'control-mouse3' : 'right mouse down',
            'shift-mouse1' : 'left mouse down', 'shift-mouse2' : 'middle mouse down', 'shift-mouse3' : 'right mouse down',
            'alt-mouse1' : 'left mouse down', 'alt-mouse2' : 'middle mouse down', 'alt-mouse3' : 'right mouse down',
            'page_down' : 'page down', 'page_down up' : 'page down up', 'page_up' : 'page up', 'page_up up' : 'page up up',
            }

        for e in keyboard_keys:
            self.accept(f'raw-{e}', self.input, [e, True])
            self.accept(f'raw-{e}-up', self.input_up, [e, True])
            self.accept(f'raw-{e}-repeat', self.input_hold, [e, True])

        self.accept('buttonDown', self.input)
        self.accept('buttonUp', self.input_up)
        self.accept('buttonHold', self.input_hold)
        self.accept('keystroke', self.text_input)
        ConfigVariableBool('paste-emit-keystrokes', False)

        self.disableMouse()
        mouse._mouse_watcher = self.mouseWatcherNode
        mouse.enabled = True
        self.mouse = mouse

        scene.set_up()
        self._update_task = taskMgr.add(self._update, "update")

        # try to load settings that need to be applied before entity creation
        application.load_settings()

        from ursina.prefabs.hot_reloader import HotReloader
        application.hot_reloader = HotReloader(__main__.__file__ if hasattr(__main__, '__file__') else 'None', enabled=application.development_mode)  # make sure it's running from a file and not an interactive session.

        try:
            from ursina import gamepad
        except e as Exception:
            print(e)

        if application.window_type != 'none':
            window.make_editor_gui()
        if 'editor_ui_enabled' in kwargs:
            window.editor_ui.enabled = kwargs['editor_ui_enabled']


    def _update(self, task):
        """Internal task that runs every frame. Updates time, mouse, sequences and entities."""
        if application.calculate_dt:
            time.dt = globalClock.getDt() * application.time_scale          # time between frames
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


    def input_up(self, key, is_raw=False):
        if not is_raw and key in keyboard_keys:
            return

        if key in ('wheel_up', 'wheel_down'):
            return

        key += ' up'
        self.input(key)


    def input_hold(self, key, is_raw=False):
        key = key.replace('control-', '')
        key = key.replace('shift-', '')
        key = key.replace('alt-', '')

        if key in self._input_name_changes:
            key = self._input_name_changes[key]

        key += ' hold'
        self.input(key)


    def input(self, key, is_raw=False):
        """Built-in input handler. Propagates the input to all entities and the input function of the main script. MAin use case for this it to simulate input though code, like: app.input('a').

        Args:
            key (Any): The input key.
            is_raw (bool, optional): Whether or not the input should be treated as "raw". Defaults to False.
        """
        if not is_raw and key in keyboard_keys:
            return

        if not 'mouse' in key:
            for prefix in ('control-', 'shift-', 'alt-'):
                if key.startswith(prefix):
                    key = key.replace('control-', '')
                    key = key.replace('shift-', '')
                    key = key.replace('alt-', '')
                    if key in keyboard_keys:
                        return

        if key in self._input_name_changes:
            key = self._input_name_changes[key]

        if key in input_handler.rebinds:
            key = input_handler.rebinds[key]

        input_handler.input(key)

        if not application.paused:
            if hasattr(__main__, 'input'):
                __main__.input(key)

        for entity in scene.entities:
            if entity.enabled == False or entity.ignore or entity.ignore_input:
                continue
            if application.paused and entity.ignore_paused == False:
                continue

            if hasattr(entity, 'input') and callable(entity.input):
                if entity.input(key):
                    break

            if hasattr(entity, 'scripts'):
                for script in entity.scripts:
                    if script.enabled and hasattr(script, 'input') and callable(script.input):
                        if script.input(key):
                            break


        mouse.input(key)


    def text_input(self, key):
        key_code = ord(key)
        if key_code < 32 or (key_code >= 127 and key_code <= 160):
            return

        if key == ' ' and input_handler.held_keys['control']:
            return

        if not application.paused:
            if hasattr(__main__, 'text_input'):
                __main__.text_input(key)

        for entity in scene.entities:
            if entity.enabled == False or entity.ignore or entity.ignore_input:
                continue
            if application.paused and entity.ignore_paused == False:
                continue

            if hasattr(entity, 'text_input') and callable(entity.text_input):
                entity.text_input(key)

            if hasattr(entity, 'scripts'):
                for script in entity.scripts:
                    if script.enabled and hasattr(script, 'text_input') and callable(script.text_input):
                        script.text_input(key)

    def step(self):     # use this control the update loop yourself. call app.step() in a while loop for example, instead of app.run()
        self.taskMgr.step()


    def run(self, info=True):
        if window.show_ursina_splash:
            from ursina.prefabs import ursina_splash

        application.load_settings()
        if info:
            print('os:', platform.system())
            print('development mode:', application.development_mode)
            print('application successfully started')

        super().run()


if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    def input(key):
        print(key)
    app.run()
