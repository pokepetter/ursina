import sys
from pathlib import Path
from panda3d.core import getModelPath


paused = False
time_scale = 1
sequences = list()
trace_entity_definition = True # enable to set entity.line_definition
print_entity_definition = False

package_folder = Path(__file__).parent
asset_folder = Path().cwd()

development_mode = True
dirs = [e.stem for e in asset_folder.iterdir() if e.is_dir()]
if 'src' in dirs and 'python' in dirs:
    development_mode = False


internal_models_folder = package_folder / 'models/'
internal_models_compressed_folder = package_folder / 'models_compressed/'
internal_prefabs_folder = package_folder / 'prefabs/'
internal_scripts_folder = package_folder / 'scripts/'
internal_textures_folder = package_folder / 'textures/'
internal_fonts_folder = package_folder / 'fonts/'

prefabs_folder = asset_folder / 'prefabs/'
scenes_folder = asset_folder / 'scenes/'
scripts_folder = asset_folder / 'scripts/'
textures_folder = asset_folder / 'textures/'
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
print('dev mode:', development_mode)

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
    try:
        from ursina import window
        with open(path) as f:
            try:
                # d = dict(locals(), **globals())
                # exec(f.read(), d, d)
                exec(f.read())
            except Exception as e:
                print('settings.py error:', e)
                pass
    except:
        print('no settings.py file')
