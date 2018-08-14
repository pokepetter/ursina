# from ursina import *
import os
import sys
from panda3d.core import Filename
from panda3d.core import getModelPath
# from ursina import main
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

        self.internal_model_folder = self.package_folder + 'internal_models/'
        self.internal_prefab_folder = self.package_folder + 'internal_prefabs/'
        self.internal_script_folder = self.package_folder + 'internal_scripts/'
        self.internal_texture_folder = self.package_folder + 'internal_textures/'
        self.internal_scene_folder = self.package_folder + 'internal_scenes/'
        self.internal_font_folder = self.package_folder + 'font/'

        self.model_folder = self.asset_folder + 'models/'
        self.prefab_folder = self.asset_folder + 'prefabs/'
        self.scene_folder = self.asset_folder + 'scenes/'
        self.script_folder = self.asset_folder + 'scripts/'
        self.texture_folder = self.asset_folder + 'textures/'

        self.compressed_texture_folder = self.texture_folder + 'compressed/'
        self.compressed_model_folder = self.model_folder + 'compressed/'

        # loader takes the first it finds, reorder if needed.
    #     self.model_path = getModelPath()
    #
    #     self.model_path.appendPath(self.internal_model_folder)
    #     self.model_path.appendPath(self.compressed_model_folder)
    #     self.model_path.appendPath(self.model_folder)
    #
    #     self.model_path.appendPath(self.internal_texture_folder)
    #     self.model_path.appendPath(self.compressed_texture_folder)
    #     self.model_path.appendPath(self.texture_folder)
    #
    #     self.model_path.appendPath(self.internal_font_folder)
    #     self.model_path.appendPath(self.asset_folder)
    #
    #
    # def append_path(self, path):
    #     self.model_path.append_path(path)
    #     print('added path:', path)


sys.modules[__name__] = Application()

if __name__ == '__main__':
    from ursina.main import Ursina
    app = Ursina()
    app.run()
