# from pandaeditor import *
import os
import sys
from panda3d.core import Filename
from panda3d.core import getModelPath
# from pandaeditor import main
from os.path import dirname
import glob
import re

class Application():

    def __init__(self):
        self.base = None
        import inspect

        # get path with correct cassing
        self.package_folder = glob.glob(re.sub(r'([^:])(?=[/\\]|$)', r'[\1]', dirname(__file__)))[0] + '/'
        self.asset_folder = dirname(os.path.abspath(sys.path[0])).replace('\\', '/') + '/'

        self.internal_model_folder = self.package_folder + 'internal_models/'
        self.internal_prefab_folder = self.package_folder + 'internal_prefabs/'
        self.internal_script_folder = self.package_folder + 'internal_scripts/'
        self.internal_texture_folder = self.package_folder + 'internal_textures/'
        self.internal_scene_folder = self.package_folder + 'internal_scenes/'

        self.model_folder = self.asset_folder + 'models/'
        self.prefab_folder = self.asset_folder + 'prefabs/'
        self.scene_folder = self.asset_folder + 'scenes/'
        self.script_folder = self.asset_folder + 'scripts/'
        self.texture_folder = self.asset_folder + 'textures/'

        self.compressed_texture_folder = self.texture_folder + 'compressed/'
        self.compressed_model_folder = self.model_folder + 'compressed/'

        # loader takes the first it finds, reorder if needed.
        model_path = getModelPath()

        model_path.appendPath(self.internal_model_folder)
        model_path.appendPath(self.compressed_model_folder)
        model_path.appendPath(self.model_folder)

        model_path.appendPath(self.internal_texture_folder)
        model_path.appendPath(self.compressed_texture_folder)
        model_path.appendPath(self.texture_folder)
        print(model_path)


sys.modules[__name__] = Application()

if __name__ == '__main__':
    from pandaeditor.main import PandaEditor
    app = PandaEditor()
