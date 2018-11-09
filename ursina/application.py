import os
import sys
from panda3d.core import getModelPath
from pathlib import Path


class Application():

    def __init__(self):
        self.package_folder = Path(__file__).parent
        self.asset_folder = Path().cwd()

        self.internal_models_folder = self.package_folder / 'internal_models/'
        self.internal_prefabs_folder = self.package_folder / 'internal_prefabs/'
        self.internal_scripts_folder = self.package_folder / 'internal_scripts/'
        self.internal_textures_folder = self.package_folder / 'internal_textures/'
        self.internal_fonts_folder = self.package_folder / 'fonts/'

        self.models_folder = self.asset_folder / 'models/'
        self.prefabs_folder = self.asset_folder / 'prefabs/'
        self.scenes_folder = self.asset_folder / 'scenes/'
        self.scripts_folder = self.asset_folder / 'scripts/'
        self.textures_folder = self.asset_folder / 'textures/'
        self.fonts_folder = self.asset_folder / 'fonts/'

        self.compressed_textures_folder = self.textures_folder / 'compressed/'
        self.compressed_models_folder = self.models_folder / 'compressed/'

        # fonts are loaded py panda3d, so add paths here
        self.model_path = getModelPath()
        self.model_path.append_path(str(self.internal_fonts_folder.resolve()))
        self.model_path.append_path(str(self.asset_folder.resolve()))

sys.modules[__name__] = Application()

if __name__ == '__main__':
    from ursina.main import Ursina
    app = Ursina()
    app.run()
