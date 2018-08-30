import os
import sys
from panda3d.core import Filename
from panda3d.core import getModelPath
from os.path import dirname
import inspect
import glob
import re

class Application():

    def __init__(self):
        self.base = None

        # get path with correct casing
        try:
            self.package_folder = glob.glob(re.sub(r'([^:])(?=[/\\]|$)', r'[\1]', dirname(__file__)))[0] + '/'
            # print('package_folder:', self.package_folder)
        except:
            self.package_folder = ''
            print('package_folder not found')
        self.asset_folder = (os.path.abspath(sys.path[0])).replace('\\', '/') + '/'

        self.internal_models_folder = self.package_folder + 'internal_models/'
        self.internal_prefabs_folder = self.package_folder + 'internal_prefabs/'
        self.internal_scripts_folder = self.package_folder + 'internal_scripts/'
        self.internal_textures_folder = self.package_folder + 'internal_textures/'
        self.internal_fonts_folder = self.package_folder + 'font/'

        self.models_folder = self.asset_folder + 'models/'
        self.prefabs_folder = self.asset_folder + 'prefabs/'
        self.scenes_folder = self.asset_folder + 'scenes/'
        self.scripts_folder = self.asset_folder + 'scripts/'
        self.textures_folder = self.asset_folder + 'textures/'

        self.compressed_textures_folder = self.textures_folder + 'compressed/'
        self.compressed_models_folder = self.models_folder + 'compressed/'


sys.modules[__name__] = Application()

if __name__ == '__main__':
    from ursina.main import Ursina
    app = Ursina()
    app.run()
