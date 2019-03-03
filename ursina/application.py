import os
import sys
from panda3d.core import getModelPath
from pathlib import Path



package_folder = Path(__file__).parent
asset_folder = Path().cwd()

internal_models_folder = package_folder / 'internal_models/'
internal_prefabs_folder = package_folder / 'internal_prefabs/'
internal_scripts_folder = package_folder / 'internal_scripts/'
internal_textures_folder = package_folder / 'internal_textures/'
internal_fonts_folder = package_folder / 'fonts/'

models_folder = asset_folder / 'models/'
prefabs_folder = asset_folder / 'prefabs/'
scenes_folder = asset_folder / 'scenes/'
scripts_folder = asset_folder / 'scripts/'
textures_folder = asset_folder / 'textures/'
fonts_folder = asset_folder / 'fonts/'

compressed_textures_folder = textures_folder / 'compressed/'
compressed_models_folder = models_folder / 'compressed/'

# fonts are loaded py panda3d, so add paths here
_model_path = getModelPath()
_model_path.append_path(str(internal_fonts_folder.resolve()))
_model_path.append_path(str(asset_folder.resolve()))
