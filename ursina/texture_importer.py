import glob
from ursina import application
from ursina.texture import Texture
from pathlib import Path


file_types = ('.jpg', '.png', '.gif')

def load_texture(name, path=None):
    folders = ( # folder search order
        application.compressed_textures_folder,
        application.asset_folder,
        application.internal_textures_folder,
        )
    if path:
        folders = (path,)

    if name.endswith('.mp4'):
        for folder in folders:
            for filename in folder.glob('**/' + name):
                # print('loaded movie texture:', filename)
                return loader.loadTexture(filename.resolve())


    for folder in folders:
        for filename in folder.glob('**/' + name + '.*'):
            if filename.suffix in file_types:
                # print('found:', filename)
                return Texture(filename.resolve())


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
    try:
        from psd_tools import PSDImage
    except Exception as e:
        return e

    if not application.compressed_textures_folder.exists():
        application.compressed_textures_folder.mkdir()


    file_type = '.*'
    if '.' in name:
        file_type = ''

    # print('searching for texture:', name + file_type)
    for f in application.asset_folder.glob('**/' + name + file_type):
        # if f.parent == application.compressed_textures_folder:
        # print('------------------', str(f.resolve()))
        if '\\compressed\\' in str(f) or f.suffix not in ('.psd', '.png', '.jpg', '.jpeg', '.gif'):
            continue
        # print('  found:', f)

        if f.suffix == '.psd':
            image = PSDImage.load(f)
            image = image.as_PIL()
        elif f.suffix == '.png':
            image = Image.open(f)
        # print(max(image.size))
        # print('............', image.mode)
        if image.mode != 'RGBA' and max(image.size) > 512:
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
