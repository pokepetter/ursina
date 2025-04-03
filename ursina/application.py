"""
ursina/application.py

This module contains global variables and functions for managing the application state,
including pausing, resuming, quitting, and loading settings. It also defines various
paths and settings used throughout the Ursina engine.

Dependencies:
- sys
- pathlib.Path
- panda3d.core.getModelPath
- ursina.string_utilities
"""

import sys
from pathlib import Path
from panda3d.core import getModelPath
from ursina import string_utilities

# Global variables for managing application state
paused = False
time_scale = 1
calculate_dt = True
sequences = []
trace_entity_definition = False  # Enable to set entity.line_definition
print_entity_definition = False

# Paths and settings
package_folder = Path(__file__).parent
asset_folder = Path(sys.argv[0]).parent
blender_paths = dict()

# Development mode settings
development_mode = True
dirs = [e.stem for e in asset_folder.parent.iterdir() if e.is_dir()]
if 'src' in dirs and 'python' in dirs:
    development_mode = False

# Window and splash settings
window_type = 'onscreen'
show_ursina_splash = False
ursina_splash = None
gltf_no_srgb = True

# Print and exception settings
print_info = development_mode
print_warnings = True
raise_exception_on_missing_model = False
raise_exception_on_missing_texture = False

# Internal folders
internal_models_folder = package_folder / 'models/'
internal_models_compressed_folder = package_folder / 'models_compressed/'
internal_scripts_folder = package_folder / 'scripts/'
internal_textures_folder = package_folder / 'textures/'
internal_fonts_folder = package_folder / 'fonts/'
internal_audio_folder = package_folder / 'audio/'

# Asset folders
scenes_folder = asset_folder / 'scenes/'
scripts_folder = asset_folder / 'scripts/'
fonts_folder = asset_folder / 'fonts/'

textures_compressed_folder = asset_folder / 'textures_compressed/'
models_compressed_folder = asset_folder / 'models_compressed/'

# Add font paths to Panda3D model path
_model_path = getModelPath()
_model_path.append_path(str(internal_fonts_folder.resolve()))
_model_path.append_path(str(Path('C:/Windows/Fonts').resolve()))
_model_path.append_path(str(asset_folder.resolve()))

# Global variables for Ursina engine
base = None  # This will be set once the Ursina() is created
hot_reloader = None  # Will be set by main if development_mode

def pause():
    """
    Pause the application.
    """
    global paused
    paused = True

def resume():
    """
    Resume the application.
    """
    global paused
    paused = False

def quit():
    """
    Quit the application.
    """
    sys.exit()

def load_settings(path=asset_folder / 'settings.py'):
    """
    Load settings from the specified settings file.

    Args:
        path (Path): The path to the settings file.

    Raises:
        Exception: If there is an error while loading the settings.
    """
    if path.exists():
        with open(path) as f:
            try:
                exec('from ursina import *\n' + f.read())
                string_utilities.print_info('loaded settings from settings.py successfully')
            except Exception as e:
                string_utilities.print_warning('warning: settings.py error:', e)
