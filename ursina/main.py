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

import os
import atexit
import socket
import subprocess
from direct.filter.CommonFilters import CommonFilters
from ursina import color
from ursina.prefabs.memory_counter import MemoryCounter
from ursina.color import tint
from ursina import Entity, Sky, EditorCamera, Func, destroy, Ursina
from GamePlusEditor.StartingUI import StartingUI
from GamePlusEditor.SceneEditor import SceneEditor
from GamePlusEditor.ProjectSaver import ProjectSaver, SceneStateSaver
from GamePlusEditor.ProjectLoader import SceneStateLoader
from GamePlusEditor.OtherStuff import CurrentFolderNameReturner, RecursivePerformer
from GamePlusEditor.OpenFile import OpenFile, SaveFile
from GamePlusEditor.CoreFiles.InstructionMenu import InstructionMenu
from GamePlusEditor.ProjectExporter import ProjectExporter
from GamePlusEditor.ProjectEditor import ProjectEditor
from GamePlusEditor.CodeEditorPython import CodeEditorPython
from GamePlusEditor.CodeEditorUrsaVisor import CodeEditorUrsaVisor
from GamePlusEditor.CoreFiles.InstructionList import InstructionList
from GamePlusEditor.CoreFiles.Terminal import Terminal

import __main__
time.dt = 0
time.dt_unscaled = 0
keyboard_keys = '1234567890qwertyuiopasdfghjklzxcvbnm'


from ursina.scripts.singleton_decorator import singleton
@singleton
class Ursina(ShowBase):
    def __init__(self, title='ursina', icon='textures/ursina.ico', borderless:bool=None, fullscreen:bool=None, size=None, forced_aspect_ratio=None, position=None, vsync=True, editor_ui_enabled:bool=None, window_type='onscreen', development_mode:bool=None, render_mode=None, show_ursina_splash=False, use_ingame_console=False, **kwargs):
        """The main class of Ursina. This class is a singleton, so you can only have one instance of it.

        Keyword Args (optional):
            title (str): The title of the window.\n
            fullscreen (bool): Whether the window should be fullscreen or not.\n
            size (tuple(int, int)): The size of the window.\n
            forced_aspect_ratio (bool): Whether the window should have a forced aspect ratio or not.\n
            position (tuple(int, int)): The position of the window. Defaults to center of main monitor.\n
            vsync (bool): Whether the window should have vsync enabled or not.\n
            borderless (bool): Whether the window should be borderless or not.\n
            show_ursina_splash (bool): Whether the Ursina splash should be shown or not.\n
            render_mode (str): The render mode of the window.\n
            development_mode (bool): Whether the development mode should be enabled or not.\n
            editor_ui_enabled (bool): Whether the editor UI should be enabled or not.\n
            window_type (str): The type of the window. Can be 'onscreen', 'offscreen' or 'none'.\n
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
        """Internal task that runs every frame. Updates time, mouse, sequences and entities."""
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

            if e.shader:
                for key, value in e.shader.continuous_input.items():
                    e.set_shader_input(key, value())

        return Task.cont


    def input_up(self, key, is_raw=False): # internal method for key release
        if not is_raw and key in keyboard_keys:
            return

        if key in ('wheel_up', 'wheel_down'):
            return

        key += ' up'
        self.input(key)


    def input_hold(self, key, is_raw=False):   # internal method for handling repeating input that occurs when you hold the key
        key = key.replace('control-', '')
        key = key.replace('shift-', '')
        key = key.replace('alt-', '')

        if key in self._input_name_changes:
            key = self._input_name_changes[key]

        key += ' hold'
        self.input(key)


    def input(self, key, is_raw=False): # internal method for handling input
        """Built-in input handler. Propagates the input to all entities and the input function of the main script. Main use case for this it to simulate input though code, like: app.input('a').

        Args:
            key (Any): The input key.
            is_raw (bool, optional): Whether or not the input should be treated as "raw". Defaults to False.
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


    def text_input(self, key):  # internal method for handling text input
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

    def step(self): # use this control the update loop yourself. call app.step() in a while loop for example, instead of app.run()
        self.taskMgr.step()


    def run(self, info=True):
        if application.show_ursina_splash:
            from ursina.prefabs.splash_screen import SplashScreen
            application.ursina_splash = SplashScreen()

        application.load_settings()
        if info:
            print('os:', platform.system())
            print('development mode:', application.development_mode)
            print('application successfully started')

        super().run()


class UrsinaEditor(Entity):
    def __init__(self, EditorCamera, **kwargs):
        super().__init__()
        self.CurrentSupportedEditors = ["Scene editor", "Code editor", "Ursa-visor editor"]
        self.AddCurrentSupportedEditors = [self.AddSceneEditor, self.AddPythonCodeEditor, self.AddUrsaVisorEditor]
        self.ProjectEditorsList: list = []
        self.CurrentProjectEditor: ProjectEditor = None
        self.CurrentTerminals: list = []
        self.CurrentOpenedGames: list = []

        self.EditorCamera = EditorCamera
        self.NonConfiableEditorDataDefault = {"CurrentProjectNames": [], "RecentEdits": []}
        self.NonConfiableEditorData = OpenFile("Non configable editor data.txt", f"{CurrentFolderNameReturner()}/Editor data", self.NonConfiableEditorDataDefault, True)
        self.InstructionList = InstructionList()

        self.ConfiableEditorDataDefault = {"Show tooltip": True, "Auto save on exit": False, "Show memory counter": True, "Fullscreen": False, "Anti-aliasing sample": 4, "Render distance (near)": .10, "Render distance (far)": 10000.0, }
        self.ConfiableEditorDataDefaultType = ("bool", "bool", "bool", "bool", "int", "float", "float")
        self.ConfiableEditorData = OpenFile("Configable editor data.txt", f"{CurrentFolderNameReturner()}/Editor data", self.ConfiableEditorDataDefault, True)
        self.FolderName = os.path.dirname(os.path.abspath(__file__))
        self.ProjectSettings = None
        self.Filter = CommonFilters(base.win, base.cam)

        self.MemoryCounter = MemoryCounter(enabled=self.ConfiableEditorData["Show memory counter"])
        self.StartingUi = StartingUI(EditorDataDictConfigable=self.ConfiableEditorData, RegiveDataDictFunc=self.RetakeDataDict, RetakeDataDictFunc=self.RegiveDataDict, EditorDataDictNonConfigable=self.NonConfiableEditorData, OnProjectStart=self.StartEdit, ChangeConfigDataToDefaultTypeFunc=self.ChangeConfigDataToDefaultType, ProjectName="", SaveNonConfiableData=self.SaveData, FuncToEnableOnOpen=self.SetupSceneOfWorkedProject, ShowInstructionFunc=self.ShowInstruction, RemoveProjectNameFunc=self.RemoveProject, ExportToPyFunc=self.ExportProjectToPy)

    def StartEdit(self):
        self.ProjectEditorsList.append(ProjectEditor(ExportToPyFunc=self.ExportProjectToPy, EditorDataDict=self.ConfiableEditorData, CurrentTabs=[], ShowInstructionFunc=self.ShowInstruction, EditorCamera=self.EditorCamera, ReadyToHostProjectFunc=self.ReadyToHostProject, HostProjectFunc=self.HostProject, enabled=True, ToAddTabsText=self.CurrentSupportedEditors, ToAddTabsFunc=self.AddCurrentSupportedEditors, PlayFunction=self.PlayProject))
        self.CurrentProjectEditor: ProjectEditor = self.ProjectEditorsList[-1]
        self.CurrentProjectEditor.SetUp()
        self.CurrentProjectEditor.ProjectName = self.StartingUi.ProjectName
        self.CurrentProjectEditor.ProjectSettings = self.StartingUi.ProjectSettings
        self.StartingUi.ProjectName = ""
        self.StartingUi.ProjectSettings = {"ProjectGraphicsQuality": "Low", "ProjectLanguage": "Python", "ProjectNetworkingOnline": False, "CurrentTargatedPlatform": "windows", "CurrentProjectBase": "FPC"}
        self.AddSceneEditor()
        self.CurrentProjectEditor.JumpTabs(0)

        self.EditorCamera.item_to_in_find_on_mouse_hit_rotate = self.CurrentProjectEditor.CurrentSceneEditor.WorldItems

        self.CurrentProjectEditor.CurrentSceneEditor.enable()
        self.CurrentProjectEditor.CurrentSceneEditor.UniversalParentEntity.enable()
        RecursivePerformer(self.CurrentProjectEditor.CurrentSceneEditor.UniversalParentEntity)

    def SetupEditor(self, Editor):
        if Editor.name.startswith("Scene"):
            Editor.MakeEditorEnvironment(application.base.camNode, (255, 255, 255, 0), (0.2399, .999, 0.1009, 0.938))
        elif Editor.name.startswith("Code"):
            Editor.SetUp()
        elif Editor.name.startswith("Ursa"):
            Editor.SetUp()

    def Save(self, SaveOnlyIfProjectAlreayExists=False):
        if self.CurrentProjectEditor is None:
            return
        ProjectSaver(ProjectName=self.CurrentProjectEditor.ProjectName, UdFunc=self.CurrentProjectEditor.UDFunc, UdVar=self.CurrentProjectEditor.UDVars, Udsrc=self.CurrentProjectEditor.UDSrc, WindowConfig=self.CurrentProjectEditor.UDWindowConfig, ToImport=list(self.CurrentProjectEditor.ToImport), Items=self.CurrentProjectEditor.CurrentSceneEditor.WorldItems, Path=f'{self.FolderName}/Current Games', GameSettings=self.CurrentProjectEditor.ProjectSettings, SaveOnlyIfProjectAlreayExists=SaveOnlyIfProjectAlreayExists)

        SceneState = self.CurrentProjectEditor.CurrentSceneEditor.GetState()
        SceneStateSaver(self.CurrentProjectEditor.ProjectName, f'{self.FolderName}/Current Games', SceneState)

        if not self.CurrentProjectEditor.ProjectName in self.NonConfiableEditorData["CurrentProjectNames"] and not SaveOnlyIfProjectAlreayExists:
            self.NonConfiableEditorData["CurrentProjectNames"].append(self.CurrentProjectEditor.ProjectName)
            self.SaveData()

    def OnExit(self):
        self.Save(True)
        for process in self.CurrentOpenedGames:
            if process.poll() is not None:
                process.terminate()

        if self.ConfiableEditorData["Auto save on exit"] and self.StartingUi.ProjectName:
            self.Save()

    def Setup(self):
        self.ConfigEditorAsSettings()
        atexit.register(self.OnExit)
        self.StartingUi.Setup()
        self.StartingUi.ShowRecentProjects(self.SetupSceneOfWorkedProject)

    def SaveData(self):
        SaveFile("Non configable editor data.txt", f"{CurrentFolderNameReturner()}/Editor data", self.NonConfiableEditorData)
        SaveFile("Configable editor data.txt", f"{CurrentFolderNameReturner()}/Editor data", self.ConfiableEditorData)

    def ChangeConfigDataToDefaultType(self, Data: dict):
        try:
            for i, j in enumerate(self.ConfiableEditorDataDefault):
                if type(self.ConfiableEditorDataDefault[j]).__name__ == "int":
                    Data[j] = int(Data[j])

                elif type(self.ConfiableEditorDataDefault[j]).__name__ == "float":
                    if Data[j].find('.') != -1:
                        Data[j] = Data[j][:Data[j].find('.') + 1] + Data[j][Data[j].find('.') + 1:].replace('.', '')
                    Data[j] = float(Data[j])

                elif type(self.ConfiableEditorDataDefault[j]).__name__ == "bool":
                    if Data[j].lower() == "true":
                        Data[j] = True
                    elif Data[j].lower() == "false":
                        Data[j] = False

                elif type(self.ConfiableEditorDataDefault[j]).__name__ == "str":
                    Data[j] = str(Data[j])

            self.ConfiableEditorData = Data
            self.ConfigEditorAsSettings()

        except Exception as e:
            print(f"{__file__}:: {e}")

    def ShowInstruction(self, Str, Color=tint(color.white, -.6), Title="Info", KillIn=1, KillAfter=5, WordWrap=40):
        self.InstructionList.append(InstructionMenu(ToSay=Str, Title=Title, Color=Color, KillIn=KillIn, killAfter=KillAfter, WordWrap=WordWrap))
        self.InstructionList[-1].CloseButton.on_click = Func(self.DestroyInstruction, self.InstructionList[-1])

    def DestroyInstruction(self, Instruction):
        self.Index = self.InstructionList.index(Instruction)
        destroy(self.InstructionList[self.Index])
        del self.InstructionList[self.Index]

    def AddTextToTerminal(self, text):
        for i in self.CurrentTerminals:
            i.AddTextToTerminal(text)

    def AddSceneEditor(self):
        def AddTerminal(ParnetEntity):
            TempTerminal = Terminal(self.AddTextToTerminal, parent=ParnetEntity)
            self.CurrentTerminals.append(TempTerminal)

            TempTerminal.Bg.scale_x = 1.35
            TempTerminal.Bg.origin = (.5, 0, 0)
            TempTerminal.UniversalParentEntity.origin = (.5, 0, 0)
            TempTerminal.UniversalParentEntity.position = Vec3(0.887, -0.3, 2)
            TempTerminal.Bg.scale = Vec3(1.35, 0.2, 1)
            TempTerminal.SetUp()

        self.CurrentProjectEditor.CurrentTabs.append(SceneEditor(enabled=True, SaveFunction=self.Save, EditorCamera=self.EditorCamera, EditorDataDict=self.ConfiableEditorData, ShowInstructionFunc=self.ShowInstruction, AddTerminalFunc=None, ParentProjectEditor=self.CurrentProjectEditor))
        self.CurrentProjectEditor.CurrentTabs[-1].AddTerminal = Func(AddTerminal, self.CurrentProjectEditor.CurrentTabs[-1].UniversalParentEntity)

        self.CurrentProjectEditor.CurrentTabs[-1].name = f"Scene Editor {len([i for i in range(len(self.CurrentProjectEditor.CurrentTabs)) if type(self.CurrentProjectEditor.CurrentTabs[i]).__name__ == 'SceneEditor'])}"
        self.CurrentProjectEditor.CurrentTabs[-1].GetPosTemp()
        self.CurrentProjectEditor.CurrentTabs[-1].Setup()

        if len(self.CurrentProjectEditor.CurrentTabs) > 1:
            self.CurrentProjectEditor.CurrentTabs[-1].WorldItems = self.CurrentProjectEditor.CurrentSceneEditor.WorldItems
            self.CurrentProjectEditor.CurrentTabs[-1].ignore = True
            self.CurrentProjectEditor.CurrentTabs[-1].disable()
            self.CurrentProjectEditor.CurrentTabs[-1].UniversalParentEntity.disable()
            RecursivePerformer(self.CurrentProjectEditor.CurrentTabs[-1].SpecialEntities, "disable")

        else:
            self.CurrentProjectEditor.CurrentSceneEditor = self.CurrentProjectEditor.CurrentTabs[-1]
            self.CurrentProjectEditor.CurrentEditor = self.CurrentProjectEditor.CurrentTabs[-1]
            self.CurrentProjectEditor.CurrentTabs[-1].enable()
            RecursivePerformer(self.CurrentProjectEditor.CurrentTabs[-1].UniversalParentEntity)
            RecursivePerformer(self.CurrentProjectEditor.CurrentTabs[-1].SpecialEntities)
            self.SetupEditor(self.CurrentProjectEditor.CurrentTabs[-1])
            self.CurrentProjectEditor.AfterSceneEditorSetUp()

        self.CurrentProjectEditor.UpdateTabsMenu()

    def AddPythonCodeEditor(self):
        self.CurrentProjectEditor.CurrentTabs.append(CodeEditorPython(ProjectName=self.CurrentProjectEditor.ProjectName, SaveFunction=self.Save, enabled=False, EditorDataDict=self.ConfiableEditorData, ignore=True, UdSrc=self.CurrentProjectEditor.UDSrc, OnFileAdded=self.CurrentProjectEditor.OnFileAdded, ShowInstructionFunc=self.ShowInstruction))

        self.CurrentProjectEditor.CurrentTabs[-1].name = f"Code Editor {len([i for i in range(len(self.CurrentProjectEditor.CurrentTabs)) if type(self.CurrentProjectEditor.CurrentTabs[i]).__name__ == 'CodeEditorPython'])}"
        self.SetupEditor(self.CurrentProjectEditor.CurrentTabs[-1])
        self.CurrentProjectEditor.UpdateTabsMenu()

    def AddUrsaVisorEditor(self):
        self.CurrentProjectEditor.CurrentTabs.append(CodeEditorUrsaVisor(enabled=False, ignore=True, SaveFunction=self.Save, EditorDataDict=self.ConfiableEditorData))

        self.CurrentProjectEditor.CurrentTabs[-1].name = f"Ursa Editor {len([i for i in range(len(self.CurrentProjectEditor.CurrentTabs)) if type(self.CurrentProjectEditor.CurrentTabs[i]).__name__ == 'CodeEditorUrsaVisor'])}"

        self.SetupEditor(self.CurrentProjectEditor.CurrentTabs[-1])
        self.CurrentProjectEditor.UpdateTabsMenu()

    def ConfigEditorAsSettings(self):
        self.StartingUi.ConfigEditorAsSettings(self.ConfiableEditorData)
        for i in range(len(self.ProjectEditorsList)):
            for j in range(len(self.ProjectEditorsList[i].CurrentTabs)):
                self.ProjectEditorsList[i].CurrentTabs[j].ConfigEditorAsSettings(self.ConfiableEditorData)

        self.MemoryCounter.enabled = self.ConfiableEditorData["Show memory counter"]
        self.StartingUi.EditorDataDict = self.ConfiableEditorData
        window.fullscreen = self.ConfiableEditorData["Fullscreen"]
        camera.clip_plane_near = self.ConfiableEditorData["Render distance (near)"]
        camera.clip_plane_far = self.ConfiableEditorData["Render distance (far)"]
        if self.ConfiableEditorData["Anti-aliasing sample"] > 0:
            self.Filter.delMSAA()
            self.Filter.setMSAA(self.ConfiableEditorData["Anti-aliasing sample"])
        else:
            self.Filter.delMSAA()

    def ExportProjectToPy(self, Path, ProjectName=None, InProjectEditor=True, Demo=False):
        if ProjectName is None:
            ProjectName = self.CurrentProjectEditor.ProjectName

        if Path != "":
            if InProjectEditor:
                self.Save()
            Path.replace("\\", "/")
            Path += "/Exported games"

            ProjectExporter(ProjectName=ProjectName, ProjectPath=f'{self.FolderName}/Current Games', ToSavePath=Path, Demo=Demo)

            self.ShowInstruction("Exported successfully", KillAfter=6, KillIn=3)
        else:
            self.ShowInstruction("Invalid path", KillAfter=6, KillIn=3, Title="Error")

    def PlayProject(self):
        self.CurrentProjectEditor.SaveProjectButton.on_click()
        self.ExportProjectToPy(CurrentFolderNameReturner(), self.CurrentProjectEditor.ProjectName, False, Demo=True)
        self.CurrentOpenedGames.append(subprocess.Popen(["python", f"{CurrentFolderNameReturner()}/Exported games/{self.CurrentProjectEditor.ProjectName}/Main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE))

    def ReadyToHostProject(self):
        self.Port = 48513
        self.Ip = "localhost"

        self.Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        return self.Port, self.Ip

    def HostProject(self, MaxJoin=0):
        self.Server.bind((self.Ip, self.Port))
        if MaxJoin != 0:
            self.Server.listen(MaxJoin)
        else:
            self.Server.listen()

    def SetupSceneOfWorkedProject(self, WorldItemsList, Project=""):
        self.StartEdit()
        for item in WorldItemsList:
            self.CurrentProjectEditor.CurrentSceneEditor.WorldItems.append(eval(item['cls'] + item['args']))
        self.SetProjectName(Project)
        print(f"Project name: {self.CurrentProjectEditor.ProjectName}")
        LoadedSceneState = SceneStateLoader(self.CurrentProjectEditor.ProjectName, f'{self.FolderName}/Current Games')
        if LoadedSceneState is not False:
            self.CurrentProjectEditor.CurrentSceneEditor.SetState(LoadedSceneState)

    def SetProjectName(self, Value: str):
        self.CurrentProjectEditor.ProjectName = Value

    def RemoveProject(self, Name, Replace=False):
        if Replace is False:
            self.NonConfiableEditorData["CurrentProjectNames"].remove(Name)
            self.NonConfiableEditorData["RecentEdits"].remove(Name)

        else:
            if Replace not in self.NonConfiableEditorData["CurrentProjectNames"]:
                self.NonConfiableEditorData["CurrentProjectNames"][self.NonConfiableEditorData["CurrentProjectNames"].index(Name)] = Replace
                self.NonConfiableEditorData["RecentEdits"][self.NonConfiableEditorData["RecentEdits"].index(Name)] = Replace

        self.SaveData()

    def RegiveDataDict(self):
        return self.ConfiableEditorData, self.NonConfiableEditorData

    def RetakeDataDict(self, ConfigableEditorData, NonConfigableEditorData):
        self.ConfiableEditorData = ConfigableEditorData
        self.NonConfigableEditorData = NonConfigableEditorData


def BaseRunner():
    app = Ursina()
    window.exit_button.disable()
    window.fps_counter.disable()
    application.development_mode = False
    window.cog_button.disable()

    Sky()
    Editor = UrsinaEditor(EditCam := EditorCamera())
    Editor.Setup()
    app.run()


if __name__ == "__main__":
    BaseRunner()
