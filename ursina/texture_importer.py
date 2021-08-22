from pathlib import Path
from copy import copy
from ursina import application
from ursina.texture import Texture


imported_textures = dict()
file_types = ('.tif', '.jpg', '.jpeg', '.png', '.gif')
textureless = False


def load_texture(name, path=None):
    if textureless:
        return None

    if name in imported_textures:
        return copy(imported_textures[name])

    folders = ( # folder search order
        application.compressed_textures_folder,
        application.asset_folder,
        application.internal_textures_folder,
        )
    if path:
        if isinstance(path, str):
            folders = (Path(path),)
        else:
            folders = (path,)

    if name.endswith('.mp4'):
        for folder in folders:
            for filename in folder.glob('**/' + name):
                # print('loaded movie texture:', filename)
                return loader.loadTexture(filename.resolve())


    for folder in folders:
        if '.' in name: # got name with file extension
            for filename in folder.glob('**/' + name):
                t = Texture(filename.resolve())
                imported_textures[name] = t
                return t

        for filename in folder.glob('**/' + name + '.*'): # no file extension given, so try all supported
            if filename.suffix in file_types:
                # print('found:', filename)
                t = Texture(filename.resolve())
                imported_textures[name] = t
                return t

    if application.development_mode:
        try:
            from psd_tools import PSDImage
        except (ModuleNotFoundError, ImportError) as e:
            print('info: psd-tools3 not installed')

        for folder in folders:
            for filename in folder.glob('**/' + name + '.psd'):
                print('found uncompressed psd, compressing it...')
                compress_textures(name)
                return load_texture(name)

    return None



def compress_textures(name=''):
    import os
    try:
        from PIL import Image
    except Exception as e:
        return e


    if not application.compressed_textures_folder.exists():
        application.compressed_textures_folder.mkdir()


    file_type = '.*'
    if '.' in name:
        file_type = ''

    # print('searching for texture:', name + file_type)
    for f in application.asset_folder.glob('**/' + name + file_type):

        if '\\textures_compressed\\' in str(f) or f.suffix not in ('.psd', '.png', '.jpg', '.jpeg', '.gif'):
            continue
        # print('  found:', f)
        image = None
        if f.suffix == '.psd':
            try:
                from psd_tools import PSDImage
            except (ModuleNotFoundError, ImportError) as e:
                print('info: psd-tools3 not installed')
                return None

            image = PSDImage.load(f)
            image = image.as_PIL()
        # elif f.suffix == '.png':
        #     image = Image.open(f)

        if not image:
            return False
        # print(max(image.size))
        # print('............', image.mode)
        if image and image.mode != 'RGBA' and max(image.size) > 512:
            image.save(
                application.compressed_textures_folder / (Path(f).stem + '.jpg'),
                'JPEG',
                quality=80,
                optimize=True,
                progressive=True
                )
            print('    compressing to jpg:', application.compressed_textures_folder / (f.stem + '.jpg'))
            continue
        else:
            image.save(application.compressed_textures_folder / (f.stem + '.png'), 'PNG')
            print('    compressing to png:', application.compressed_textures_folder / (f.stem + '.png'))



if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    Entity(model='quad', texture='white_cube')
    app.run()
