# from pandaeditor import *
import os
import sys
from panda3d.core import Filename
from panda3d.core import getModelPath

class Application():

    def __init__(self):
        self.base = None

        self.asset_folder = os.path.dirname(os.path.dirname(__file__))

        self.internal_model_folder = Filename.fromOsSpecific(os.path.join(
            os.path.dirname(__file__),
            'internal_models/'
            ))
        self.internal_prefab_folder = Filename.fromOsSpecific(os.path.join(
            os.path.dirname(__file__),
            'internal_prefabs/'
            ))
        self.internal_script_folder = Filename.fromOsSpecific(os.path.join(
            os.path.dirname(__file__),
            'internal_scripts/'
            ))
        self.internal_texture_folder = Filename.fromOsSpecific(os.path.join(
            os.path.dirname(__file__),
            'internal_textures/'
            ))
        self.internal_scene_folder = Filename.fromOsSpecific(os.path.join(
            os.path.dirname(__file__),
            'internal_scenes/'
            ))


        self.model_folder = Filename.fromOsSpecific(os.path.join(
            self.asset_folder,
            'models/'
            ))
        self.prefab_folder = Filename.fromOsSpecific(os.path.join(
            self.asset_folder,
            'prefabs/'
            ))
        self.scene_folder = Filename.fromOsSpecific(os.path.join(
            self.asset_folder,
            'scenes/'
            ))
        self.script_folder = Filename.fromOsSpecific(os.path.join(
            self.asset_folder,
            'scripts/'
            ))
        self.texture_folder = Filename.fromOsSpecific(os.path.join(
            self.asset_folder,
            'textures/'
            ))

        self.compressed_texture_folder = Filename.fromOsSpecific(os.path.join(
            self.texture_folder,
            'compressed/'
            ))
        self.compressed_model_folder = Filename.fromOsSpecific(os.path.join(
            self.model_folder,
            'compressed/'
            ))

        # loader takes the first it finds, reorder if needed.
        model_path = getModelPath()
        model_path.appendPath(self.internal_texture_folder)
        model_path.appendPath(self.compressed_texture_folder)
        model_path.appendPath(self.texture_folder)

        model_path.appendPath(self.internal_model_folder)
        model_path.appendPath(self.compressed_model_folder)
        model_path.appendPath(self.model_folder)


sys.modules[__name__] = Application()
