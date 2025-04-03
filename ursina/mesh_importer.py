"""
ursina/mesh_importer.py

This module provides functions for loading and importing 3D models into the Ursina engine.
It supports various file formats such as .bam, .ursinamesh, .obj, .glb, .gltf, and .blend.
The module also includes functions for converting Blender files to OBJ format and loading Blender scenes.

Dependencies:
- os
- platform
- subprocess
- copy
- pathlib.Path
- ursina.mesh.Mesh
- ursina.application
- ursina.color
- time.perf_counter
- ursina.string_utilities.print_info
- ursina.string_utilities.print_warning
- ursina.vec3.Vec3
- panda3d.core
- gltf
- builtins
- ursina.sequence.Func
"""

import os
import platform
import subprocess
from copy import copy, deepcopy
from pathlib import Path
from ursina.mesh import Mesh
from ursina import application, color
from time import perf_counter
from ursina.string_utilities import print_info, print_warning
from ursina.vec3 import Vec3
import panda3d.core as p3d
import gltf
import builtins
from ursina.sequence import Func
from ursina import application

imported_meshes = dict()
blender_scenes = dict()
# folders = (application.asset_folder, )

def load_model(name, folder=None, file_types=('.bam', '.ursinamesh', '.obj', '.glb', '.gltf', '.blend'),
               use_deepcopy=False, gltf_no_srgb=Func(getattr, application, 'gltf_no_srgb')):
    """
    Load a 3D model from the specified folder and file types.

    Args:
        name (str): The name of the model to load.
        folder (Path, optional): The folder to search for the model. Defaults to None.
        file_types (tuple, optional): The file types to search for. Defaults to ('.bam', '.ursinamesh', '.obj', '.glb', '.gltf', '.blend').
        use_deepcopy (bool, optional): Whether to use deepcopy for the model. Defaults to False.
        gltf_no_srgb (Func, optional): Function to determine if GLTF should use sRGB. Defaults to Func(getattr, application, 'gltf_no_srgb').

    Returns:
        NodePath: The loaded model as a Panda3D NodePath.

    Raises:
        TypeError: If the name is not a string or the folder is not a Path.
        Exception: If there is an error loading a .ursinamesh file.
    """
    if callable(gltf_no_srgb):
        gltf_no_srgb = gltf_no_srgb()

    if not isinstance(name, str):
        raise TypeError(f"Argument save must be of type str, not {type(name)}")
        
    if '.' in name:
        full_name = name
        name = full_name.split('.')[0]
        file_types = ('.' + full_name.split('.', 1)[1],)

    if name in imported_meshes:
        # print('load cached model', name)
        try:
            instance = copy(imported_meshes[name]) if not use_deepcopy else deepcopy(imported_meshes[name])
            instance.clearTexture()
            return instance
        except:
            pass

    if folder is not None:
        if not isinstance(folder, Path):
            raise TypeError(f'folder must be a Path, not a {type(folder)}')
        _folders = (folder,)
    else:
        _folders = (application.models_compressed_folder, application.asset_folder, application.internal_models_compressed_folder)

    for filetype in file_types:
        if use_deepcopy and filetype == '.bam':
            continue
        for folder in _folders:
            # warning: glob is case-insensitive on windows, so m.path will be all lowercase
            for file_path in folder.glob(f'**/{name}{filetype}'):
                if filetype == '.bam':
                    # print_info('loading bam')
                    return builtins.loader.loadModel(file_path)  # type: ignore

                if filetype in ('.gltf', '.glb'):
                    gltf_settings = gltf.GltfSettings()
                    gltf_settings.no_srgb = gltf_no_srgb
                    model_root = gltf.load_model(str(file_path), gltf_settings=gltf_settings)
                    imported_meshes[name] = p3d.NodePath(model_root)
                    return p3d.NodePath(model_root)

                if filetype == '.ursinamesh':
                    try:
                        with open(file_path) as f:
                            m = eval(f.read())
                            m.path = file_path
                            m.name = name
                            m.vertices = [Vec3(*v) for v in m.vertices]
                            imported_meshes[name] = m
                            return m
                    except:
                        raise Exception('invalid ursinamesh file:', file_path)

                if filetype == '.obj':
                    # print('found obj', file_path)
                    m = obj_to_ursinamesh(folder=folder, name=name, return_mesh=True)
                    m.path = file_path
                    m.name = name
                    imported_meshes[name] = m
                    if not use_deepcopy:
                        m.save(f'{name}.bam')
                    return m

                elif filetype == '.blend':
                    print_info('found blend file:', file_path)
                    if blend_to_obj(file_path):
                        # obj_to_ursinamesh(name=name)
                        return load_model(name, folder, use_deepcopy=use_deepcopy)
                else:
                    try:
                        return builtins.loader.loadModel(file_path)  # type: ignore
                    except:
                        pass

    return None


# find blender installations
if application.development_mode:
    if platform.system() == 'Windows':
        # get blender path by getting default program for '.blend' file extension
        import shlex
        import winreg
        try:
            class_root = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, '.blend')
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, fr'{class_root}\shell\open\command') as key:
                command = winreg.QueryValueEx(key, '')[0]
                default_blender = shlex.split(command)[0]
                default_blender = Path(default_blender)
                application.blender_paths['default'] = default_blender
                blender_foundation_directory = default_blender.parent.parent
                for blender_installation in blender_foundation_directory.glob('*'):
                    first_folder = tuple(blender_installation.glob('*'))[0]  # version
                    version_name = first_folder.name[:3]
                    blender_path = list(blender_installation.glob('blender.exe'))[0]
                    if application.blender_paths['default'] == blender_path:
                        continue
                    application.blender_paths[version_name] = blender_path
        except:
            pass

    elif platform.system() == 'Linux':
        # Use "which" command to find blender
        which_process = subprocess.run(('which', 'blender'), stdout=subprocess.PIPE)
        if which_process.returncode == 0:
            blender_exec = which_process.stdout.decode().strip()
            application.blender_paths['default'] = blender_exec


def load_blender_scene(name, path=Func(getattr, application, 'asset_folder'), reload=False, skip_hidden=True,
                       models_only=False, uvs=True, vertex_colors=True, normals=True, triangulate=True, decimals=4):
    """
    Load a Blender scene and convert it to Ursina format.

    Args:
        name (str): The name of the Blender scene to load.
        path (Path, optional): The path to the Blender file. Defaults to Func(getattr, application, 'asset_folder').
        reload (bool, optional): Whether to reload the scene if it already exists. Defaults to False.
        skip_hidden (bool, optional): Whether to skip hidden objects. Defaults to True.
        models_only (bool, optional): Whether to load only models. Defaults to False.
        uvs (bool, optional): Whether to include UVs. Defaults to True.
        vertex_colors (bool, optional): Whether to include vertex colors. Defaults to True.
        normals (bool, optional): Whether to include normals. Defaults to True.
        triangulate (bool, optional): Whether to triangulate the mesh. Defaults to True.
        decimals (int, optional): The number of decimal places for vertex coordinates. Defaults to 4.

    Returns:
        dict: The loaded Blender scene as a dictionary.

    Raises:
        ValueError: If no Blender file is found at the specified path.
    """
    if callable(path):
        path = path()

    scenes_folder = Path(application.asset_folder / 'scenes')
    if not scenes_folder.exists():
        scenes_folder.mkdir()

    out_file_path = scenes_folder / f'{name}.ursina_blender_scene'
    # print('loading:', out_file_path)
    if reload or not out_file_path.exists():
        print_info('reload:')
        blend_file = tuple(path.glob(f'**/{name}.blend'))
        if not blend_file:
            raise ValueError('no blender file found at:', path / name)
        blend_file = blend_file[0]
        print_info('loading blender scene:', blend_file, '-->', out_file_path)

        args = [
            get_blender(blend_file),
            blend_file,
            '--background',
            '--python',
            application.internal_scripts_folder / '_blender_scene_to_ursina.py',
            out_file_path,
            '--skip_hidden' if skip_hidden else '',
            '--models_only' if models_only else '',
            '--uvs' if uvs else '',
            '--normals' if normals else '',
            '--vertex_colors' if vertex_colors else '',
            '--triangulate' if triangulate else '',
            f'--decimals={decimals}',
        ]
        subprocess.run(args)

    with open(out_file_path) as f:
        file_content = f.read()
        loc = {}
        exec(file_content, globals(), loc)
        if models_only:
            blender_scenes[name] = loc['meshes']
            return loc['meshes']
        blender_scenes[name] = loc['scene_parent']
        return loc['scene_parent']


def get_blender(blend_file):
    """
    Get the path to the Blender executable for the specified Blender file.

    Args:
        blend_file (Path): The path to the Blender file.

    Returns:
        Path: The path to the Blender executable.

    Raises:
        Warning: If no Blender installation is found.
    """
    if not application.blender_paths:
        print_warning(f"Error: Trying to load .blend file, but no blender installation was found. blender_paths: {application.blender_paths}. If Blender is not installed, install it. If Blender is installed, but not found, make sure to install it to the default install location. If it's still not found, you can provide a custom path like this: application.blender_paths['default'] = Path('C:\\Program Files\\...')")
        return None

    if len(application.blender_paths) == 1:
        return application.blender_paths['default']

    with open(blend_file, 'rb') as f:
        try:
            blender_version_number = (f.read(12).decode("utf-8", "strict"))[-3:]  # get version from start of .blend file e.g. 'BLENDER-v280'
            blender_version_number = blender_version_number[0] + '.' + blender_version_number[1:2]
            print_info('blender_version:', blender_version_number)
            if blender_version_number in application.blender_paths:
                return application.blender_paths[blender_version_number]
            print_info('using default blender version')
            return application.blender_paths['default']
        except:
            print_info('using default blender version')
            return application.blender_paths['default']


def blend_to_obj(blend_file: Path, out_folder=Func(getattr, application, 'models_compressed_folder'), export_mtl=True):
    """
    Convert a Blender file to OBJ format.

    Args:
        blend_file (Path): The path to the Blender file.
        out_folder (Path, optional): The folder to save the OBJ file. Defaults to Func(getattr, application, 'models_compressed_folder').
        export_mtl (bool, optional): Whether to export the MTL file. Defaults to True.

    Returns:
        list: A list of exported Blender files.
    """
    if callable(out_folder):
        out_folder = out_folder()

    if not out_folder.exists():
        out_folder.mkdir()

    export_script_path = application.internal_scripts_folder / '_blend_export.py'
    exported = []
    export_mtl_arg = '--export_mtl' if export_mtl else ''

    blender = get_blender(blend_file)

    name = f'{blend_file.stem}.obj'
    out_file_path = out_folder / name
    print_info('converting .blend file to .obj:', blend_file, '-->', out_file_path, 'using:', blender)

    if platform.system() == 'Windows':
        subprocess.call(f'''"{blender}" "{blend_file}" --background --python "{export_script_path}" {export_mtl_arg} "{out_file_path}"''')
    else:
        subprocess.run((blender, blend_file, '--background', '--python', export_script_path, export_mtl_arg, out_file_path))

    exported.append(blend_file)
    return exported


def obj_to_ursinamesh(folder=Func(getattr, application, 'models_compressed_folder'),
                      out_folder=Func(getattr, application, 'models_compressed_folder'),
                      name='*', return_mesh=True, save_to_file=False, delete_obj=False):
    """
    Convert an OBJ file to Ursina Mesh format.

    Args:
        folder (Path, optional): The folder containing the OBJ file. Defaults to Func(getattr, application, 'models_compressed_folder').
        out_folder (Path, optional): The folder to save the Ursina Mesh file. Defaults to Func(getattr, application, 'models_compressed_folder').
        name (str, optional): The name of the OBJ file. Defaults to '*'.
        return_mesh (bool, optional): Whether to return the mesh. Defaults to True.
        save_to_file (bool, optional): Whether to save the mesh to a file. Defaults to False.
        delete_obj (bool, optional): Whether to delete the OBJ file after conversion. Defaults to False.

    Returns:
        Mesh: The converted Ursina Mesh.

    Raises:
        Warning: If there is an error in the OBJ file.
    """
    if callable(folder):
        folder = folder()
    if callable(out_folder):
        out_folder = out_folder()

    if name.endswith('.obj'):
        name = name[:-4]

    for file_path in folder.glob(f'**/{name}.obj'):
        print('read obj at:', file_path)
        with file_path.open('r') as file:
            lines = file.readlines()

        verts = []
        tris = []

        uv_indices = []
        uvs = []
        norm_indices = []
        norms = []
        normals = []  # final normals made getting norms with norm_indices

        vertex_colors = []
        vertex_colors_packed = []
        current_color = None
        mtl_data = None
        mtl_dict = {}

        # parse the obj file to a Mesh
        for i, l in enumerate(lines):
            if l.startswith('v '):
                parts = [float(v) for v in l[2:].strip().split(' ')]
                vert = parts[:3]
                vert[0] = -vert[0]
                verts.append(tuple(vert))
                if len(parts) > 3:
                    vertex_colors_packed.append(color.rgb(*parts[3:]))
            elif l.startswith('vn '):
                n = l[3:].strip().split(' ')
                norms.append(tuple(float(e) for e in n))
            elif l.startswith('vt '):
                uv = l[3:].strip().split(' ')
                uvs.append(tuple(float(e) for e in uv))
            elif l.startswith('f '):
                l = l[2:].split(' ')
                try:
                    tri = tuple(int(t.split('/')[0]) - 1 for t in l if t != '\n')
                except:
                    print_warning('error in obj file line:', i, ':', l)
                    return
                if len(tri) == 3:
                    tris.extend(tri)
                    if current_color:
                        vertex_colors.extend([current_color] * 3)
                    elif vertex_colors_packed:
                        vertex_colors.extend([vertex_colors_packed[idx] if idx < len(vertex_colors_packed) else color.white for idx in tri])
                elif len(tri) == 4:
                    tris.extend((tri[0], tri[1], tri[2], tri[2], tri[3], tri[0]))
                    if current_color:
                        vertex_colors.extend([current_color] * 6)
                    elif vertex_colors_packed:
                        vertex_colors.extend([vertex_colors_packed[idx] for idx in (tri[0], tri[1], tri[2], tri[2], tri[3], tri[0])])
                else:  # ngon
                    for i in range(1, len(tri) - 1):
                        tris.extend((tri[i], tri[i + 1], tri[0]))
                    if current_color:
                        vertex_colors.extend([current_color] * len(tri))
                    elif vertex_colors_packed:
                        for i in range(1, len(tri) - 1):
                            vertex_colors.extend([vertex_colors_packed[idx] for idx in (tri[i], tri[i + 1], tri[0])])
                try:
                    uv = tuple(int(t.split('/')[1]) - 1 for t in l)
                    if len(uv) == 3:
                        uv_indices.extend(uv)
                    elif len(uv) == 4:
                        uv_indices.extend((uv[0], uv[1], uv[2], uv[2], uv[3], uv[0]))
                    else:  # ngon
                        for i in range(1, len(uv) - 1):
                            uv_indices.extend((uv[i], uv[i + 1], uv[0]))
                except:
                    pass
                try:
                    n = tuple(int(t.split('/')[2]) - 1 for t in l)
                    if len(n) == 3:
                        norm_indices.extend(n)
                    elif len(n) == 4:
                        norm_indices.extend((n[0], n[1], n[2], n[2], n[3], n[0]))
                    else:  # ngon
                        for i in range(1, len(n) - 1):
                            norm_indices.extend((n[i], n[i + 1], n[0]))
                except:
                    pass
            elif l.startswith('mtllib '):  # load mtl file
                mtl_file_name = file_path.with_suffix('.mtl')
                if mtl_file_name.exists():
                    with open(mtl_file_name, mode='r', encoding='utf-8') as mtl_file:
                        mtl_data = mtl_file.readlines()
                        for i in range(len(mtl_data) - 1):
                            if mtl_data[i].startswith('newmtl '):
                                material_name = mtl_data[i].strip()[7:]  # remove 'newmtl '
                                for j in range(i + 1, min(i + 8, len(mtl_data))):
                                    if mtl_data[j].startswith('newmtl'):
                                        break
                                    if mtl_data[j].startswith('Kd '):
                                        material_color = [float(e) for e in mtl_data[j].strip()[3:].split(' ')]
                                        mtl_dict[material_name] = (*material_color, 1)
            elif l.startswith('usemtl ') and mtl_data:  # apply material color
                material_name = l[7:].strip()  # remove 'usemtl '
                if material_name in mtl_dict:
                    current_color = mtl_dict[material_name]

        if norms:  # make sure we have normals and not just normal indices (weird edge case).
            normals = [(-norms[nid][0], norms[nid][1], norms[nid][2]) for nid in norm_indices]

        if return_mesh:
            return Mesh(
                vertices=[verts[t] for t in tris],
                normals=normals,
                uvs=[uvs[uid] for uid in uv_indices],
                colors=vertex_colors
            )

        mesh = Mesh(vertices=tuple(verts[t] for t in tris),
                    colors=tuple(col for col in vertex_colors),
                    uvs=tuple(uvs[uid] for uid in uv_indices),
                    normals=normals)

        if not save_to_file:
            return mesh

        out_path = (out_folder / file_path.stem).with_suffix('.ursinamesh')
        mesh.save(folder=out_folder, name=f'{file_path.stem}.ursinamesh')

        if delete_obj:
            os.remove((out_folder / file_path.stem).with_suffix('.obj'))

        print_info('saved ursinamesh to:', out_path)


# faster, but does not apply modifiers
def blend_to_obj_fast(model_name=None, write_to_disk=False):
    """
    Convert a Blender file to OBJ format using the tinyblend library.

    Args:
        model_name (str, optional): The name of the model to convert. Defaults to None.
        write_to_disk (bool, optional): Whether to write the OBJ file to disk. Defaults to False.

    Returns:
        str: The converted OBJ file content.
    """
    print_info('find models')
    from tinyblend import BlenderFile  # type: ignore
    application.models_compressed_folder.mkdir(parents=True, exist_ok=True)
    files = os.listdir(application.models_folder)
    for f in files:
        if f.endswith('.blend'):
            print('compress______', f)
            blend = BlenderFile(application.models_folder + '/' + f)
            number_of_objects = len(blend.list('Object'))
            for o in blend.list('Object'):
                if not o.data.mvert:
                    continue
                object_name = o.id.name.decode("utf-8").replace(".", "_")[2:]
                object_name = object_name.split('\0', 1)[0]
                print('name:', object_name)
                verts = [v.co for v in o.data.mvert]
                verts = tuple(verts)
                file_content = 'Mesh(' + str(verts)
                file_name = ''.join([f.split('.')[0], '.ursinamesh'])
                if number_of_objects > 1:
                    file_name = ''.join([f.split('.')[0], '_', object_name, '.ursinamesh'])
                file_path = os.path.join(application.models_compressed_folder, file_name)
                print(file_path)
                tris = tuple(triindex.v for triindex in o.data.mloop)
                flippedtris = []
                for i in range(0, len(tris) - 3, 3):
                    flippedtris.append(tris[i + 2])
                    flippedtris.append(tris[i + 1])
                    flippedtris.append(tris[i + 0])
                file_content += ', triangles=' + str(flippedtris)
                if o.data.mloopuv:
                    uvs = tuple(v.uv for v in o.data.mloopuv)
                    file_content += ', uvs=' + str(uvs)
                file_content += ''', mode='triangle')'''
                if write_to_disk:
                    with open(file_path, 'w') as file:
                        file.write(file_content)
                return file_content


def ursina_mesh_to_obj(mesh, name='', out_path=Func(getattr, application, 'models_compressed_folder'),
                        max_decimals=5, flip_faces=True):
    """
    Convert a Ursina Mesh to OBJ format.

    Args:
        mesh (Mesh): The Ursina Mesh to convert.
        name (str, optional): The name of the OBJ file. Defaults to ''.
        out_path (Path, optional): The folder to save the OBJ file. Defaults to Func(getattr, application, 'models_compressed_folder').
        max_decimals (int, optional): The maximum number of decimal places for vertex coordinates. Defaults to 5.
        flip_faces (bool, optional): Whether to flip the faces of the mesh. Defaults to True.
    """
    if callable(out_path):
        out_path = out_path()

    from ursina.string_utilities import camel_to_snake
    obj = ''
    obj += f'mtllib {name}.mtl\n'
    obj += f'usemtl {name}\n'
    if not name:
        name = camel_to_snake(mesh.__class__.__name__)
    obj += 'o ' + name + '\n'
    verts = mesh.vertices
    for v in verts:
        v = [round(e, max_decimals) for e in v]
        obj += f'v {v[0]} {v[1]} {v[2]}\n'
    if mesh.uvs:
        for uv in mesh.uvs:
            uv = [round(e, max_decimals) for e in uv]
            obj += f'vt {uv[0]} {uv[1]}\n'
    obj += 's off\n'
    if mesh.triangles:
        tris = mesh.triangles
        if isinstance(tris[0], tuple):  # convert from tuples to flat
            new_tris = []
            for t in tris:
                if len(t) == 3:
                    new_tris.extend(t[::-1] if flip_faces else t)
                elif len(t) == 4:  # turn quad into tris
                    new_tris.extend((t[2], t[1], t[0]) if flip_faces else (t[0], t[1], t[2]))
                    new_tris.extend((t[0], t[3], t[2]) if flip_faces else (t[2], t[3], t[0]))
            tris = new_tris
    if mesh.mode == 'ngon':
        tris = []
        for i in range(1, len(mesh.vertices) - 1):
            tris.extend((i, i + 1, 0))
    # tris must be a list of indices
    for i, t in enumerate(tris):
        if i % 3 == 0:
            obj += '\nf '
        obj += str(t + 1)
        if mesh.uvs:
            obj += '/' + str(t + 1)
        obj += ' '
    obj += '\n'
    with open(out_path / (name + '.obj'), 'w') as f:
        f.write(obj)
        print_info('saved obj:', out_path / (name + '.obj'))


def compress_internal():
    """
    Compress internal models by converting Blender files to OBJ format and then to Ursina Mesh format.
    """
    for blend_file in application.internal_models_folder.glob('*.blend'):
        blend_to_obj(blend_file, export_mtl=False)
        obj_to_ursinamesh(application.internal_models_compressed_folder,
                          application.internal_models_compressed_folder,
                          return_mesh=False, save_to_file=True, delete_obj=True)


if __name__ == '__main__':
    compress_internal()
    from ursina import *
    from ursina import Ursina, Entity, EditorCamera, Sky
    app = Ursina()
    m = obj_to_ursinamesh(folder=application.asset_folder.parent / 'samples', name='procedural_rock_0',
                           save_to_file=False, delete_obj=False)
    print(m.serialize())
    EditorCamera()
    Sky(texture='sky_sunset')
    app.run()
