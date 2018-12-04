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

    return None

if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    Entity(model='quad', texture='white_cube')
    app.run()


def compress_textures(name=None):
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


    files = os.listdir(application.textures_folder)
    compressed_files = os.listdir(application.compressed_textures_folder)

    for f in files:
        if f.endswith('.psd') or f.endswith('.png'):
            if name:
                if not name in f:
                    continue
            try:
                # print('f:', application.compressed_textures_folder + f)
                if f.suffix == '.psd':
                    image = PSDImage.load(application.textures_folder / f)
                    image = image.as_PIL()
                else:
                    image = Image.open(application.textures_folder / f)
                # print(max(image.size))
                if max(image.size) > 512:
                    image.save(
                        application.compressed_textures_folder / (f[:-4] + '.jpg'),
                        'JPEG',
                        quality=80,
                        optimize=True,
                        progressive=True
                        )
                    print('compressing to jpg:', f)
                else:
                    image.save(
                        application.compressed_textures_folder / (f[:-4] + '.png'),
                        'PNG'
                        )
                    print('compressing to png:', f)
            except Exception as e:
                print(e)
        # elif f.endswith('.png'):
