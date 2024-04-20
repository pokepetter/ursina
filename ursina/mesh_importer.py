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


imported_meshes = dict()
blender_scenes = dict()

def load_model(name, path=Func(getattr, application, 'asset_folder'), file_types=('.bam', '.ursinamesh', '.obj', '.glb', '.gltf', '.blend'), use_deepcopy=False, gltf_no_srgb=Func(getattr, application, 'gltf_no_srgb')):
    if callable(path):
        path = path()
    if callable(gltf_no_srgb):
        gltf_no_srgb = gltf_no_srgb()

    if not isinstance(name, str):
        raise TypeError(f"Argument save must be of type str, not {type(str)}")

    if '.' in name:
        full_name = name
        name = full_name.split('.')[0]
        file_types = ('.' + full_name.split('.',1)[1],)

    if name in imported_meshes:
        # print('load cached model', name)
        try:
            if not use_deepcopy:
                instance = copy(imported_meshes[name])
            else:
                instance = deepcopy(imported_meshes[name])

            instance.clearTexture()
            return instance

        except:
            pass

    for filetype in file_types:
        if use_deepcopy and filetype == '.bam':
            continue
        # warning: glob is case-insensitive on windows, so m.path will be all lowercase
        for filename in path.glob(f'**/{name}{filetype}'):
            if filetype == '.bam':
                # print_info('loading bam')
                return builtins.loader.loadModel(filename)  # type: ignore

            if filetype == '.gltf' or filetype == '.glb':
                gltf_settings = gltf.GltfSettings()
                gltf_settings.no_srgb = gltf_no_srgb
                model_root = gltf.load_model(str(filename), gltf_settings=gltf_settings)
                imported_meshes[name] = p3d.NodePath(model_root)
                return p3d.NodePath(model_root)

            if filetype == '.ursinamesh':
                try:
                    with open(filename) as f:
                        m = eval(f.read())
                        m.path = filename
                        m.name = name
                        m.vertices = [Vec3(*v) for v in m.vertices]
                        imported_meshes[name] = m
                        return m
                except:
                    print_warning('invalid ursinamesh file:', filename)


            if filetype == '.obj':
                # print('found obj', filename)
                m = obj_to_ursinamesh(path=path, name=name, return_mesh=True)
                m.path = filename
                m.name = name
                imported_meshes[name] = m
                if not use_deepcopy:
                    m.save(f'{name}.bam')

                return m

            elif filetype == '.blend':
                print_info('found blend file:', filename)
                if compress_models(path=path, name=name):
                    # obj_to_ursinamesh(name=name)
                    return load_model(name, path, use_deepcopy=use_deepcopy)
            else:
                try:
                    return builtins.loader.loadModel(filename)  # type: ignore
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
                    first_folder = tuple(blender_installation.glob('*'))[0] # version
                    version_name = first_folder.name[:3]
                    blender_path = list(blender_installation.glob('blender.exe'))[0]
                    if application.blender_path['default'] == blender_path:
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


def load_blender_scene(name, path=Func(getattr, application, 'asset_folder'), reload=False, skip_hidden=True, models_only=False, uvs=True, vertex_colors=True, normals=True, triangulate=True, decimals=4):
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



def get_blender(blend_file):    # try to get a matching blender version in case we have multiple blender version installed
    if not application.blender_paths:
        raise Exception('error: trying to load .blend file, but no blender installation was found. blender_paths:', application.blender_paths)

    if len(application.blender_paths) == 1:
        return application.blender_paths['default']

    with open(blend_file, 'rb') as f:
        try:
            blender_version_number = (f.read(12).decode("utf-8"))[-3:]   # get version from start of .blend file e.g. 'BLENDER-v280'
            blender_version_number = blender_version_number[0] + '.' + blender_version_number[1:2]
            print_info('blender_version:', blender_version_number)
            if blender_version_number in application.blender_paths:
                return application.blender_paths[blender_version_number]

            print_info('using default blender version')
            return application.blender_paths['default']
        except:
            print_info('using default blender version')
            return application.blender_paths['default']


def compress_models(path=None, out_path=Func(getattr, application, 'compressed_models_folder'), name='*'):
    if callable(out_path):
        out_path = out_path()

    if "/" in name or '\\' in name:
        raise Exception(f'Path character "/" or "\\" found in blender name ({name}). To successfully import .blend files, use only the file name.')

    if not application.compressed_models_folder.exists():
        application.compressed_models_folder.mkdir()

    export_script_path = application.internal_scripts_folder / '_blend_export.py'
    exported = []

    for blend_file in path.glob(f'**/{name}.blend'):
        blender = get_blender(blend_file)

        out_file_path = out_path / (blend_file.stem + '.obj')
        print_info('converting .blend file to .obj:', blend_file, '-->', out_file_path, 'using:', blender)

        if platform.system() == 'Windows':
            subprocess.call(f'''"{blender}" "{blend_file}" --background --python "{export_script_path}" "{out_file_path}"''')
        else:
            subprocess.run((blender, blend_file, '--background', '--python', export_script_path, out_file_path))

        exported.append(blend_file)

    return exported


def obj_to_ursinamesh(path=Func(getattr, application, 'compressed_models_folder'), out_path=Func(getattr, application, 'compressed_models_folder'), name='*', return_mesh=True, save_to_file=False, delete_obj=False):
    if callable(path):
        path = path()
    if callable(out_path):
        out_path = out_path()

    if name.endswith('.obj'):
        name = name[:-4]

    for f in path.glob(f'**/{name}.obj'):
        # filepath = path / (os.path.splitext(f)[0] + '.obj')
        print('read obj at:', f)


        with f.open('r') as file:
            lines = file.readlines()

        verts = []
        tris = []

        uv_indices = []
        uvs = []
        norm_indices = []
        norms = []
        normals = [] # final normals made getting norms with norm_indices

        vertex_colors = []
        vertex_colors_packed = []
        current_color = None
        mtl_data = None
        mtl_dict = {}

        # parse the obj file to a Mesh
        for i, l in enumerate(lines):  # noqa: E741
            if l.startswith('v '):
                parts = [float(v) for v in l[2:].strip().split(' ')]
                vert = parts[:3]
                vert[0] = -vert[0]
                verts.append(tuple(vert))
                if len(parts) > 3:
                    # current_color = color.rgb(*parts[3:])
                    vertex_colors_packed.append(color.rgb(*parts[3:]))

            elif l.startswith('vn '):
                n = l[3:].strip().split(' ')
                norms.append(tuple(float(e) for e in n))

            elif l.startswith('vt '):
                uv = l[3:].strip()
                uv = uv.split(' ')
                uvs.append(tuple(float(e) for e in uv))

            elif l.startswith('f '):
                l = l[2:]  # noqa: E741
                l = l.split(' ')  # noqa: E741

                try:
                    tri = tuple(int(t.split('/')[0])-1 for t in l if t != '\n')
                except:
                    print_warning('error in obj file line:', i, ':', l)
                    return
                if len(tri) == 3:
                    tris.extend(tri)
                    if current_color:
                        vertex_colors.extend([current_color for i in range(3)])
                    elif vertex_colors_packed:
                        vertex_colors.extend([vertex_colors_packed[idx] for idx in tri])

                elif len(tri) == 4:
                    tris.extend((tri[0], tri[1], tri[2], tri[2], tri[3], tri[0]))
                    if current_color:
                        vertex_colors.extend([current_color for i in range(6)])
                    elif vertex_colors_packed:
                        vertex_colors.extend([vertex_colors_packed[idx] for idx in (tri[0], tri[1], tri[2], tri[2], tri[3], tri[0])])

                else: # ngon
                    for i in range(1, len(tri)-1):
                        tris.extend((tri[i], tri[i+1], tri[0]))
                    if current_color:
                        vertex_colors.extend([current_color for i in range(len(tri))])
                    elif vertex_colors_packed:
                        for i in range(1, len(tri)-1):
                            vertex_colors.extend([vertex_colors_packed[idx] for idx in (tri[i], tri[i+1], tri[0])])

                try:
                    uv = tuple(int(t.split('/')[1])-1 for t in l)
                    if len(uv) == 3:
                        uv_indices.extend(uv)
                    elif len(uv) == 4:
                        uv_indices.extend((uv[0], uv[1], uv[2], uv[2], uv[3], uv[0]))
                    else: # ngon
                        for i in range(1, len(uv)-1):
                            uv_indices.extend((uv[i], uv[i+1], uv[0]))
                except: # if no uvs
                    pass

                try:
                    n = tuple(int(t.split('/')[2])-1 for t in l)
                    if len(n) == 3:
                        norm_indices.extend(n)
                    elif len(uv) == 4:
                        norm_indices.extend((n[0], n[1], n[2], n[2], n[3], n[0]))
                    else: # ngon
                        for i in range(1, len(n)-1):
                            norm_indices.extend((n[i], n[i+1], n[0]))
                except: # if no normals
                    pass

            elif l.startswith('mtllib '):    # load mtl file
                mtl_file_name = Path(f).with_suffix('.mtl')
                if mtl_file_name.exists():
                    with open(mtl_file_name) as mtl_file:
                        mtl_data = mtl_file.readlines()

                        for i in range(len(mtl_data)-1):
                            if mtl_data[i].startswith('newmtl '):
                                material_name = mtl_data[i].strip()[7:] # remove 'newmtl '
                                for j in range(i+1, min(i+8, len(mtl_data))):
                                    if mtl_data[j].startswith('newmtl'):
                                        break
                                    if mtl_data[j].startswith('Kd '):
                                        material_color = [float(e) for e in mtl_data[j].strip()[3:].split(' ')]
                                        mtl_dict[material_name] = *material_color, 1


            elif l.startswith('usemtl ') and mtl_data: # apply material color
                material_name = l[7:].strip()    # remove 'usemtl '
                if material_name in mtl_dict:
                    current_color = mtl_dict[material_name]


        if norms: # make sure we have normals and not just normal indices (weird edge case).
            normals = [(-norms[nid][0], norms[nid][1], norms[nid][2]) for nid in norm_indices]

        if return_mesh:
            return Mesh(
                vertices=[verts[t] for t in tris],
                normals=normals,
                uvs=[uvs[uid] for uid in uv_indices],
                colors=vertex_colors
            )

        meshstring = ''
        meshstring += 'Mesh('

        meshstring += '\nvertices='
        meshstring += str(tuple(verts[t] for t in tris))

        if vertex_colors:
            meshstring += '\ncolors='
            meshstring += str(tuple(col for col in vertex_colors))

        if uv_indices:
            meshstring += ', \nuvs='
            meshstring += str(tuple(uvs[uid] for uid in uv_indices))

        if normals:
            meshstring += ', \nnormals='
            meshstring += str(normals)

        meshstring += ''', \nmode='triangle')'''

        if not save_to_file:
            return meshstring

        out_path = out_path / (os.path.splitext(f)[0] + '.ursinamesh')
        with open(out_path, 'w') as file:
            file.write(meshstring)

        if delete_obj:
            os.remove(out_path)

        print_info('saved ursinamesh to:', out_path)

# faster, but does not apply modifiers
def compress_models_fast(model_name=None, write_to_disk=False):
    print_info('find models')
    from tinyblend import BlenderFile  # type: ignore
    application.compressed_models_folder.mkdir(parents=True, exist_ok=True)

    files = os.listdir(application.models_folder)

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

                verts = [v.co for v in o.data.mvert]
                verts = tuple(verts)

                file_content = 'Mesh(' + str(verts)

                file_name = ''.join([f.split('.')[0], '.ursinamesh'])
                if number_of_objects > 1:
                    file_name = ''.join([f.split('.')[0], '_', object_name, '.ursinamesh'])
                file_path = os.path.join(application.compressed_models_folder, file_name)
                print(file_path)

                tris = tuple(triindex.v for triindex in o.data.mloop)
                flippedtris = []
                for i in range(0, len(tris)-3, 3):
                    flippedtris.append(tris[i+2])
                    flippedtris.append(tris[i+1])
                    flippedtris.append(tris[i+0])

                file_content += ', triangles=' + str(flippedtris)

                if o.data.mloopuv:
                    uvs = tuple(v.uv for v in o.data.mloopuv)
                    file_content += ', uvs=' + str(uvs)

                file_content += ''', mode='triangle')'''

                if write_to_disk:
                    with open(file_path, 'w') as file:
                        file.write(file_content)

                return file_content

def ursina_mesh_to_obj(mesh, name='', out_path=Func(getattr, application, 'compressed_models_folder'), max_decimals=5, flip_faces=True):
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

        if isinstance(tris[0], tuple): # convert from tuples to flat
            new_tris = []
            for t in tris:
                if len(t) == 3:
                    if not flip_faces:
                        new_tris.extend([t[0], t[1], t[2]])
                    else:
                        new_tris.extend([t[2], t[1], t[0]])
                elif len(t) == 4: # turn quad into tris
                    if not flip_faces:
                        new_tris.extend([t[0], t[1], t[2], t[2], t[3], t[0]])
                    else:
                        new_tris.extend([t[2], t[1], t[0], t[0], t[3], t[2]])

            tris = new_tris


    if mesh.mode == 'ngon':
        tris = []
        for i in range(1, len(mesh.vertices)-1):
            tris.extend((i, i+1, 0))


    # tris must be a list of indices
    for i, t in enumerate(tris):
        if i % 3 == 0:
            obj += '\nf '
        obj += str(t+1)
        if mesh.uvs:
            obj += '/'+str(t+1)
        obj += ' '

    obj += '\n'
    # print(obj)
    with open(out_path / (name + '.obj'), 'w') as f:
        f.write(obj)
        print_info('saved obj:', out_path / (name + '.obj'))



def compress_internal():
    compress_models(application.internal_models_folder)
    obj_to_ursinamesh(
        application.internal_models_compressed_folder,
        application.internal_models_compressed_folder,
        return_mesh=False, save_to_file=True, delete_obj=True
        )


if __name__ == '__main__':
    # compress_internal()
    from ursina import *
    from ursina import Ursina, Entity, EditorCamera, Sky
    app = Ursina()
    # print('imported_meshes:\n', imported_meshes)
    # Entity(model='quad').model.save('quad.bam')
    # m = obj_to_ursinamesh(path=application.asset_folder.parent / 'samples', name='procedural_rock_0')
    # Entity(model=m)
    # EditorCamera()


    # application.asset_folder = application.asset_folder.parent / 'samples'
    # application.asset_folder = Path(r'C:\\Users\\Petter\\Downloads\\')
    # Entity(model='c1a0')
    # from ursina.shaders import lit_with_shadows_shader
    # Entity.default_shader = lit_with_shadows_shader
    # Entity(model='race')
    # Entity(model='ambulance', x=1.5)

    application.asset_folder = Path(r'''C:\Users\Petter\Downloads''')
    t = perf_counter()
    Entity(model='untitled')
    print('-------', perf_counter() - t)
    m = load_model('cube', use_deepcopy=True)
    # ground = Entity(model='plane', scale=10, texture='brick', texture_scale=Vec2(4))
    # DirectionalLight()

    # blender_scene = load_blender_scene(path=application.asset_folder, name='desert', reload=True)
    # blender_scene = load_blender_scene(path=application.asset_folder, name='blender_level_editor_test_scene_2')
    # print('-------', time.time() - t)

    # print('--------', blender_scene.children)
    # for e in blender_scene.children:
    #     # e.color = color.random_color()
    #     e.shader = rim_shader
    #     e.texture='matcap_4'
    #
    #
    # blender_scene.Plane_002.collider = 'mesh'
    # from ursina.prefabs.first_person_controller import FirstPersonController
    # player = FirstPersonController()

    # def input(key):
    #     if key == '+':
    #         for e in blender_scene.children:
    #             e.texture_scale = Vec2(e.texture_scale[0], e.texture_scale[1]+.1)
    #     if key == '-':
    #         for e in blender_scene.children:
    #             e.texture_scale = Vec2(e.texture_scale[0], e.texture_scale[1]-.1)
    #         print(blender_scene.children[0].texture_scale)
    #
    EditorCamera()
    Sky(texture='sky_sunset')
    # def update():
    #     blender_scene.Cube.x += (held_keys['d'] - held_keys['a']) * time.dt * 10


    app.run()
    # e = Entity(model=Cylinder(16))
    # ursina_mesh_to_obj(e.model, name='quad_export_test')
