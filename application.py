from pandaeditor import *

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
        self.internal_textures_folder = Filename.fromOsSpecific(os.path.join(
            os.path.dirname(__file__),
            'internal_textures/'
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


        print('internal_model_folder:', self.internal_model_folder)
        print('model_folder:', self.model_folder)
        print('texture_folder:', self.texture_folder)
        print('prefab_folder:', self.prefab_folder)
        print('scene_folder:', self.scene_folder)


sys.modules[__name__] = Application()
