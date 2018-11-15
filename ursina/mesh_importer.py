import os
import glob
import subprocess
from ursina.mesh import Mesh
from ursina import application
import pathlib

def load_model(path, name):
    for filename in path.glob(f'**/{name}.ursinamesh'):
        try:
            with open(filename) as f:
                m = eval(f.read())
                return m
        except:
            print('invalid ursinamesh file:', filename)

    return None


def compress_models(path=application.models_folder, outpath=application.compressed_models_folder, name='*'):
    if not application.compressed_models_folder.exists():
        application.compressed_models_folder.mkdir()

    blender_path = r"C:\Program Files\Blender Foundation\Blender\blender.exe"
    export_script_path = application.internal_scripts_folder / 'blend_export.py'

    for f in path.glob(f'**/{name}.blend'):
        outfile = outpath / f
        print('compress______', outfile)
        subprocess.call(
            r'''{} {} --background --python {}'''.format(blender_path, str(outfile), export_script_path))


def obj_to_ursinamesh(path=application.compressed_models_folder, outpath=application.compressed_models_folder, name='*', delete_obj=True):
    for f in path.glob(f'**/{name}.obj'):
        filepath = path / (os.path.splitext(f)[0] + '.obj')
        print('read obj at:', filepath)
        meshstring = ''
        meshstring += 'Mesh('

        with open(filepath, 'r') as file:
            lines = file.readlines()

        if delete_obj:
            os.remove(filepath)

        verts = list()
        tris = list()

        uv_indices = list()
        uvs = list()

        # parse the obj file to a Mesh
        for l in lines:
            if l.startswith('v '):
                vert = [float(v) for v in l[2:].strip().split(' ')]
                vert[0] = -vert[0]
                verts.append(tuple(vert))

            elif l.startswith('vt '):
                uv = l[3:].strip()
                uv = uv.split(' ')
                uvs.append(tuple([float(e) for e in uv]))

            elif l.startswith('f '):
                l = l[2:]
                l = l.split(' ')

                tri = tuple([int(t.split('/')[0]) for t in l])
                for t in tri:
                    tris.append(t-1)

                try:
                    uv = tuple([int(t.split('/')[1]) for t in l])
                    for t in uv:
                        uv_indices.append(t-1)
                except: # if no uvs
                    pass


        meshstring += '\nvertices='
        meshstring += str(tuple([verts[t] for t in tris]))

        if uv_indices:
            meshstring += ', \nuvs='
            meshstring += str(tuple([uvs[uid] for uid in uv_indices]))

        meshstring += ''', \nmode='triangle')'''
        outfilepath = outpath / (os.path.splitext(f)[0] + '.ursinamesh')
        with open(outfilepath, 'w') as file:
            file.write(meshstring)
        print('saved ursinamesh to:', outfilepath)

# faster, but does not apply modifiers
def compress_models_fast(model_name=None):
    print('find models')
    from tinyblend import BlenderFile
    if not application.compressed_models_folder.exists():
        application.compressed_models_folder.mkdir()

    files = os.listdir(application.models_folder)
    compressed_files = os.listdir(application.compressed_models_folder)

    for f in files:
        if f.endswith('.blend'):
            # print('f:', application.compressed_models_folder + '/' + f)
            print('compress______', f)
            blend = BlenderFile(application.models_folder + '/' + f)
            number_of_objects = len(blend.list('Object'))

            for o in blend.list('Object'):
                if not o.data.mvert:
                    continue
                # print(o.id.name.decode("utf-8", "strict"))
                object_name = o.id.name.decode( "utf-8").replace(".", "_")[2:]
                object_name = object_name.split('\0', 1)[0]
                print('name:', object_name)

                vertices= o.data.mvert
                verts = [v.co for v in o.data.mvert]
                verts = tuple(verts)

                file_content = 'Mesh(' + str(verts)

                file_name = ''.join([f.split('.')[0], '.ursinamesh'])
                if number_of_objects > 1:
                    file_name = ''.join([f.split('.')[0], '_', object_name, '.ursinamesh'])
                file_path = os.path.join(application.compressed_models_folder, file_name)
                print(file_path)

                tris = tuple([triindex.v for triindex in o.data.mloop])
                flippedtris = list()
                for i in range(0, len(tris)-3, 3):
                    flippedtris.append(tris[i+2])
                    flippedtris.append(tris[i+1])
                    flippedtris.append(tris[i+0])

                file_content += ', triangles=' + str(flippedtris)

                if o.data.mloopuv:
                    uvs = tuple([v.uv for v in o.data.mloopuv])
                    file_content += ', uvs=' + str(uvs)

                file_content += ''', mode='triangle')'''

                with open(file_path, 'w') as file:
                    file.write(file_content)

def compress_internal():
    compress_models(application.internal_models_folder)
    obj_to_ursinamesh(
        application.internal_models_folder / 'compressed',
        application.internal_models_folder / 'compressed',
        )


if __name__ == '__main__':
    compress_internal()
