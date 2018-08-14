import glob
from ursina import application

file_types = ('.jpg', '.png', '.gif')

def load_texture(name, path=None):
    folders = ( # folder search order
        application.compressed_texture_folder,
        application.asset_folder,
        application.internal_texture_folder,
        )
    if path:
        folders = (path)

    for folder in folders:
        for filename in glob.iglob(folder + '**/' + name + '.*', recursive=True):
            for ft in file_types:
                if filename.endswith(ft):
                    return filename

    return None

if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    Entity(model='quad', texture = 'project_browser_bg')
    app.run()

def compress_textures(name=None):
    import os
    from PIL import Image
    from os.path import dirname
    from psd_tools import PSDImage

    if not os.path.exists(application.compressed_texture_folder):
        os.makedirs(application.compressed_texture_folder)


    files = os.listdir(application.texture_folder)
    compressed_files = os.listdir(application.compressed_texture_folder)

    for f in files:
        if f.endswith('.psd') or f.endswith('.png'):
            if name:
                if not name in f:
                    continue
            try:
                # print('f:', application.compressed_texture_folder + f)
                if f.endswith('.psd'):
                    image = PSDImage.load(application.texture_folder + f)
                    image = image.as_PIL()
                else:
                    image = Image.open(application.texture_folder + f)
                # print(max(image.size))
                if max(image.size) > 512:
                    image.save(
                        application.compressed_texture_folder + f[:-4] + '.jpg',
                        'JPEG',
                        quality=80,
                        optimize=True,
                        progressive=True
                        )
                    print('compressing to jpg:', f)
                else:
                    image.save(
                        application.compressed_texture_folder + f[:-4] + '.png',
                        'PNG'
                        )
                    print('compressing to png:', f)
            except Exception as e:
                print(e)
        # elif f.endswith('.png'):
