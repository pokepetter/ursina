"""
ursina/main.py

This module defines the main Ursina class, which is responsible for initializing and managing the Ursina engine.
It handles window settings, input events, and the main update loop.

Dependencies:
- direct.showbase.ShowBase
- direct.task.Task
- panda3d.core.ConfigVariableBool
- ursina.window
- ursina.application
- ursina.input_handler
- ursina.scene
- ursina.camera
- ursina.mouse
- ursina.entity
- ursina.shader
- ursina.scripts.singleton_decorator
"""

import time
import platform

from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from panda3d.core import ConfigVariableBool

from ursina.window import instance as window
from ursina import application
from ursina import input_handler
from ursina.scene import instance as scene
from ursina.camera import instance as camera
from ursina.mouse import instance as mouse
from ursina import entity
from ursina import shader


import __main__
time.dt = 0
time.dt_unscaled = 0
keyboard_keys = '1234567890qwertyuiopasdfghjklzxcvbnm'


from ursina.scripts.singleton_decorator import singleton
@singleton
class Ursina(ShowBase):
    """
    The main class of Ursina. This class is a singleton, so you can only have one instance of it.

    Attributes:
        title (str): The title of the window.
        icon (str): The icon of the window.
        borderless (bool): Whether the window should be borderless or not.
        fullscreen (bool): Whether the window should be fullscreen or not.
        size (tuple): The size of the window.
        forced_aspect_ratio (float): The forced aspect ratio of the window.
        position (tuple): The position of the window.
        vsync (bool): Whether the window should have vsync enabled or not.
        editor_ui_enabled (bool): Whether the editor UI should be enabled or not.
        window_type (str): The type of the window.
        development_mode (bool): Whether the development mode should be enabled or not.
        render_mode (str): The render mode of the window.
        show_ursina_splash (bool): Whether the Ursina splash should be shown or not.
        use_ingame_console (bool): Whether the in-game console should be used or not.
    """

    def __init__(self, title='ursina', icon='textures/ursina.ico', borderless:bool=None, fullscreen:bool=None, size=None, forced_aspect_ratio=None, position=None, vsync=True, editor_ui_enabled:bool=None, window_type='onscreen', development_mode:bool=None, render_mode=None, show_ursina_splash=False, use_ingame_console=False, **kwargs):
        """
        Initialize the Ursina engine.

        Args:
            title (str): The title of the window.
            icon (str): The icon of the window.
            borderless (bool, optional): Whether the window should be borderless. Defaults to None.
            fullscreen (bool, optional): Whether the window should be fullscreen. Defaults to None.
            size (tuple, optional): The size of the window. Defaults to None.
            forced_aspect_ratio (float, optional): The forced aspect ratio of the window. Defaults to None.
            position (tuple, optional): The position of the window. Defaults to None.
            vsync (bool, optional): Whether the window should have vsync enabled. Defaults to True.
            editor_ui_enabled (bool, optional): Whether the editor UI should be enabled. Defaults to None.
            window_type (str, optional): The type of the window. Defaults to 'onscreen'.
            development_mode (bool, optional): Whether the development mode should be enabled. Defaults to None.
            render_mode (str, optional): The render mode of the window. Defaults to None.
            show_ursina_splash (bool, optional): Whether the Ursina splash should be shown. Defaults to False.
            use_ingame_console (bool, optional): Whether the in-game console should be used. Defaults to False.
            **kwargs: Additional keyword arguments.
        """
        entity._warn_if_ursina_not_instantiated = False
        application.window_type = window_type
        application.base = self
        if development_mode is not None:
            application.development_mode = development_mode
            
        application.show_ursina_splash = show_ursina_splash

        try:
            import gltf
            gltf.patch_loader(self.loader)
        except:
            pass

        if 'gltf_no_srgb' in kwargs:
            application.gltf_no_srgb = kwargs['gltf_no_srgb']

        if editor_ui_enabled is None:
            editor_ui_enabled = bool(application.development_mode)

        if fullscreen is None and not application.development_mode:
            fullscreen = True
            if borderless is None:
                borderless = True

        window.ready(title=title, icon=icon,
            borderless=borderless, fullscreen=fullscreen, size=size, forced_aspect_ratio=forced_aspect_ratio, position=position, vsync=vsync, window_type=window_type,
            editor_ui_enabled=editor_ui_enabled, render_mode=render_mode)

        super().__init__(windowType=application.window_type)
        window.apply_settings()
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
            'control-alt-mouse1' : 'left mouse down', 'control-alt-mouse2' : 'middle mouse down', 'control-alt-mouse3' : 'right mouse down',
            'shift-control-alt-mouse1' : 'left mouse down', 'shift-control-alt-mouse2' : 'middle mouse down', 'shift-control-alt-mouse3' : 'right mouse down',
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
        self._update_task = self.taskMgr.add(self._update, "update")

        # try to load settings that need to be applied before entity creation
        application.load_settings()

        from ursina.prefabs.hot_reloader import HotReloader
        application.hot_reloader = HotReloader(__main__.__file__ if hasattr(__main__, '__file__') else 'None', enabled=application.development_mode)  # make sure it's running from a file and not an interactive session.

        try:
            from ursina import gamepad
        except Exception as e:
            print(e)

        if application.window_type != 'none':
            window.make_editor_gui()
            if use_ingame_console:
                import builtins
                from ursina import Entity, TextField, color
                window.console = Entity(parent=window.editor_ui, position=window.top_left, z=-999, eternal=True)
                window.console.text_field = TextField(parent=window.console, scale=.75, font='VeraMono.ttf', max_lines=20, position=(0,0), register_mouse_input=True, text_input=None, eternal=True)
                window.console.text_field.bg.color = color.black66
                window.console.text_field.bg.scale_x = 1.5
                def _custom_print(*args, **kwargs):  # makes print() poutput to the in-game console instead of the terminal if use_ingame_console is True
                    content = ' '.join([str(e) for e in args])
                    if 'error' in content:
                        content = f'{content}'
                    window.console.text_field.cursor.y = window.console.text_field.text.count('\n')
                    window.console.text_field.cursor.x = 999
                    window.console.text_field.add_text(f'\n{content}')
                    window.console.text_field.scroll_to_bottom(1)
                    window.console.text_field.render()
                builtins.print = _custom_print

                def _console_text_input(key):
                    if key == '|':
                        window.console.text_field.enabled = not window.console.text_field.enabled
                window.console.text_input = _console_text_input

        print('package_folder:', application.package_folder)
        print('asset_folder:', application.asset_folder)

        entity._Ursina_instance = self


    def _update(self, task):
        """
        Internal task that runs every frame. Updates time, mouse, sequences and entities.

        Args:
            task (Task): The task object.

        Returns:
            Task.cont: Continue the task.
        """
        if application.calculate_dt:
            time.dt_unscaled = globalClock.getDt()
            time.dt = time.dt_unscaled * application.time_scale          # time between frames
        mouse.update()

        if hasattr(__main__, 'update') and __main__.update and not application.paused:
            __main__.update()

        for seq in application.sequences:
            seq.update()

        for e in scene.entities:
            if not e.enabled or e.ignore:
                continue
            if application.paused and e.ignore_paused is False:
                continue
            if e.has_disabled_ancestor():
                continue

            if hasattr(e, 'update') and callable(e.update):
                e.update()

            if hasattr(e, 'scripts'):
                for script in e.scripts:
                    if script.enabled and hasattr(script, 'update') and callable(script.update):
                        script.update()

            if e.shader and hasattr(e.shader, "continuous_input"):
                for key, value in e.shader.continuous_input.items():
                    e.set_shader_input(key, value())

        return Task.cont


    def input_up(self, key, is_raw=False):
        """
        Internal method for key release.

        Args:
            key (str): The input key.
            is_raw (bool, optional): Whether the input is raw. Defaults to False.
        """
        if not is_raw and key in keyboard_keys:
            return

        if key in ('wheel_up', 'wheel_down'):
            return

        key += ' up'
        self.input(key)


    def input_hold(self, key, is_raw=False):
        """
        Internal method for handling repeating input that occurs when you hold the key.

        Args:
            key (str): The input key.
            is_raw (bool, optional): Whether the input is raw. Defaults to False.
        """
        key = key.replace('control-', '')
        key = key.replace('shift-', '')
        key = key.replace('alt-', '')

        if key in self._input_name_changes:
            key = self._input_name_changes[key]

        key += ' hold'
        self.input(key)


    def input(self, key, is_raw=False):
        """
        Built-in input handler. Propagates the input to all entities and the input function of the main script.
        Main use case for this it to simulate input though code, like: app.input('a').

        Args:
            key (str): The input key.
            is_raw (bool, optional): Whether the input is raw. Defaults to False.
        """
        if not is_raw and key in keyboard_keys:
            return

        if 'mouse' not in key:
            for prefix in ('control-', 'shift-', 'alt-'):
                if key.startswith(prefix):
                    key = key.replace('control-', '')
                    key = key.replace('shift-', '')
                    key = key.replace('alt-', '')
                    if key in keyboard_keys:
                        return

        if key in self._input_name_changes:
            key = self._input_name_changes[key]

        # since we can rebind one key to multiple, get a list of keys
        bound_keys = input_handler.rebinds.get(key, (key, ))

        for key in bound_keys:
            input_handler.input(key)

        if not application.paused:
            if hasattr(__main__, 'input'):
                for key in bound_keys:
                    __main__.input(key)

        break_outer = False


        for e in scene.entities:
            if e.enabled is False or e.ignore or e.ignore_input:
                continue
            if application.paused and e.ignore_paused is False:
                continue
            if e.has_disabled_ancestor():
                continue

            if break_outer:
                break

            if hasattr(e, 'input') and callable(e.input):
                for key in bound_keys:
                    if break_outer:
                        break
                    if e.input(key):    # if the input function returns True, eat the input
                        break_outer = True
                        break

            if hasattr(e, 'scripts'):
                if break_outer:
                    break

                for script in e.scripts:
                    if break_outer:
                        break

                    if script.enabled and hasattr(script, 'input') and callable(script.input):
                        for key in bound_keys:
                            if script.input(key): # if the input function returns True, eat the input
                                break_outer = True
                                break

        for key in bound_keys:
            mouse.input(key)


    def text_input(self, key):
        """
        Internal method for handling text input.

        Args:
            key (str): The input key.
        """
        key_code = ord(key)
        if key_code < 32 or (key_code >= 127 and key_code <= 160):
            return

        if key == ' ' and input_handler.held_keys['control']:
            return

        if not application.paused:
            if hasattr(__main__, 'text_input'):
                __main__.text_input(key)

        for e in scene.entities:
            if e.enabled is False or e.ignore or e.ignore_input:
                continue
            if application.paused and e.ignore_paused is False:
                continue

            if hasattr(e, 'text_input') and callable(e.text_input):
                e.text_input(key)

            if hasattr(e, 'scripts'):
                for script in e.scripts:
                    if script.enabled and hasattr(script, 'text_input') and callable(script.text_input):
                        script.text_input(key)


    def step(self):
        """
        Use this to control the update loop yourself. Call app.step() in a while loop for example, instead of app.run().
        """
        self.taskMgr.step()


    def run(self, info=True):
        """
        Run the Ursina engine.

        Args:
            info (bool, optional): Whether to print information about the application. Defaults to True.
        """
        if application.show_ursina_splash:
            from ursina.prefabs.splash_screen import SplashScreen
            application.ursina_splash = SplashScreen()

        application.load_settings()
        if info:
            print('os:', platform.system())
            print('development mode:', application.development_mode)
            print('application successfully started')

        super().run()


if __name__ == '__main__':
    from ursina import *
    app = Ursina(
        # development_mode=False, 
        # use_ingame_console=True
    )
    def input(key):
        print(key)
    app.run()
