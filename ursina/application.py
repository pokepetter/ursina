import sys
from pathlib import Path
from panda3d.core import getModelPath
from ursina import string_utilities

paused = False
time_scale = 1
sequences = []
trace_entity_definition = False # enable to set entity.line_definition
print_entity_definition = False

package_folder = Path(__file__).parent
asset_folder = Path(sys.argv[0]).parent
blender_paths = {}

development_mode = True
dirs = [e.stem for e in asset_folder.parent.iterdir() if e.is_dir()]
if 'src' in dirs and 'python' in dirs:
    development_mode = False

print_info = development_mode
print_warnings = True
raise_exception_on_missing_model = False
raise_exception_on_missing_texture = False

internal_models_folder = package_folder / 'models/'
internal_models_compressed_folder = package_folder / 'models_compressed/'
internal_prefabs_folder = package_folder / 'prefabs/'
internal_scripts_folder = package_folder / 'scripts/'
internal_textures_folder = package_folder / 'textures/'
internal_fonts_folder = package_folder / 'fonts/'
internal_audio_folder = package_folder / 'audio/'

scenes_folder = asset_folder / 'scenes/'
scripts_folder = asset_folder / 'scripts/'
fonts_folder = asset_folder / 'fonts/'

compressed_textures_folder = asset_folder / 'textures_compressed/'
compressed_models_folder = asset_folder / 'models_compressed/'

# fonts are loaded py panda3d, so add paths here
_model_path = getModelPath()
_model_path.append_path(str(internal_fonts_folder.resolve()))
_model_path.append_path(str(Path('C:/Windows/Fonts').resolve()))
_model_path.append_path(str(asset_folder.resolve()))

print('package_folder:', package_folder)
print('asset_folder:', asset_folder)

base = None             # this will be set once the Ursina() is created
hot_reloader = None     # will be set my main if development_mode

def pause():
    global paused
    paused = True
    for seq in sequences:
        seq.pause()

def resume():
    global paused
    paused = False
    for seq in sequences:
        seq.resume()

def quit():
    from ursina import invoke
    invoke(sys.exit, delay=.01)


def load_settings(path=asset_folder / 'settings.py'):
    if path.exists():
        with open(path) as f:
            try:
                # d = dict(locals(), **globals())
                # exec(f.read(), d, d)
                exec('from ursina import *\n' + f.read())
                string_utilities.print_info('loaded settings from settings.py successfully')
            except Exception as e:
                string_utilities.print_warning('warning: settings.py error:', e)
