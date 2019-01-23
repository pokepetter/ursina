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
        folders = (path)

    for folder in folders:
        for filename in glob.iglob(str(folder.resolve()) + '/**/' + name + '.*', recursive=True):
            for ft in file_types:
                if filename.endswith(ft):
                    return Texture(filename)

            if filename.endswith('.psd'):
                print('found uncompressed psd, compressing it...')
                compress_textures(name)
                return load_texture(name)

    return None

if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    Entity(model='quad', texture='white_cube')
    app.run()


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

    print('searching for texture:', name + file_type)
    for f in glob.iglob(str(application.asset_folder) + '/**/' + name + file_type, recursive=True):
        if f.split(name)[0].endswith('compressed\\'):
            continue
        print('  found:', f)

        if f.endswith('.psd'):
            image = PSDImage.load(f)
            image = image.as_PIL()
        elif f.endswith('.png'):
            image = Image.open(f)
        # print(max(image.size))
        if max(image.size) > 512:
            image.save(
                application.compressed_textures_folder / (Path(f).stem + '.jpg'),
                'JPEG',
                quality=80,
                optimize=True,
                progressive=True
                )
            print('    compressing to jpg:', application.compressed_textures_folder / (Path(f).stem + '.jpg'))
            continue
        else:
            image.save(
                application.compressed_textures_folder / (Path(f).stem + '.png'),
                'PNG'
                )
            print('    compressing to png:', application.compressed_textures_folder / (Path(f).stem + '.png'))
        # elif f.endswith('.png'):
