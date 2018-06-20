from modulefinder import ModuleFinder
import os
import sys
from hurry.filesize import size
import shutil
from shutil import copy, copyfile


def copy_python():
    size = 0
    python_exec_files = [f for f in os.listdir(python_folder) if os.path.isfile(os.path.join(python_folder, f))]
    for f in python_exec_files:
        # print(f)
        file_path = os.path.join(python_folder, f)
        copy(file_path, build_folder + '/python/' + f)
        size += os.stat(file_path).st_size
    return size

def copy_python_lib():
    size = 0
    lib_folder = (os.path.dirname(sys.executable)).replace('\\', '/') + '/Lib/'
    print('LIBFOLDER:', lib_folder)
    lib_files = [f for f in os.listdir(lib_folder) if os.path.isfile(os.path.join(lib_folder, f))]
    for f in lib_files:
        file_path = os.path.join(lib_folder, f)
        copy(file_path, build_folder + '/python/Lib/' + f)
        print('copied:', f)
        size += os.stat(file_path).st_size
    return size

def copy_always_included():
    size = 0
    always_include = (
        python_folder + '/Lib/collections/',
        python_folder + '/Lib/ctypes/',
        python_folder + '/Lib/encodings/',
        python_folder + '/Lib/importlib/',

        python_folder + '/Lib/site-packages/panda3d/etc/',
        python_folder + '/Lib/site-packages/panda3d/__init__.py',
        python_folder + '/Lib/site-packages/panda3d/cg.dll',
        python_folder + '/Lib/site-packages/panda3d/cgGL.dll',
        python_folder + '/Lib/site-packages/panda3d/libp3direct.dll',
        python_folder + '/Lib/site-packages/panda3d/libp3dtool.dll',
        python_folder + '/Lib/site-packages/panda3d/libp3dtoolconfig.dll',
        python_folder + '/Lib/site-packages/panda3d/libp3interrogatedb.dll',
        python_folder + '/Lib/site-packages/panda3d/libp3openal_audio.dll',
        python_folder + '/Lib/site-packages/panda3d/libp3windisplay.dll',
        python_folder + '/Lib/site-packages/panda3d/libpanda.dll',
        python_folder + '/Lib/site-packages/panda3d/libpandaegg.dll',
        python_folder + '/Lib/site-packages/panda3d/libpandaexpress.dll',
        python_folder + '/Lib/site-packages/panda3d/libpandagl.dll',

        )
    for path in always_include:
        try:
            dest = build_folder + '/python' + path.split(python_folder)[1]
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if os.path.isfile(path):
                copy(path, dest)
                size += os.stat(path).st_size
                print('copied file:', path)
            elif os.path.isdir(path):
                copytree(path, dest)
                size += os.stat(path).st_size
                print('copied folder:', path)
        except Exception as e:
            print(e)
    return size

def copy_ursina():
    import importlib
    spec = importlib.util.find_spec('ursina')
    ursina_path = os.path.dirname(spec.origin)
    dest = build_folder + '/python/Lib/site-packages/ursina'
    os.makedirs(dest, exist_ok=True)
    copytree(ursina_path, dest)
    print('copied folder:', ursina_path)
    return os.stat(ursina_path).st_size


def copy_found_modules():
    size = 0
    finder = ModuleFinder()
    finder.run_script(project_folder + '/main.py')

    moduleslist = {}
    for name, mod in finder.modules.items():
        filename = mod.__file__

        if filename is None:
            continue
        if '__' in name:
            print('ignore:', filename)
            continue

        size += os.path.getsize(mod.__file__)

        if 'Python' in filename and 'DLLs' in filename:
            copy(filename, build_folder + '/python/DLLs')
            print('copied python dll:', filename)

        elif 'lib\\site-packages\\' in filename:
            forward_slashed = filename.split('lib\\site-packages\\')[1].replace('\\', '/')
            os.makedirs(os.path.dirname(build_folder + '/python/lib/site-packages/' + forward_slashed), exist_ok=True)
            copy(filename, build_folder + '/python/lib/site-packages/' + forward_slashed)
            print('copied from package:', forward_slashed)
    return size

def copy_assets():
    size = 0
    for f in os.listdir(project_folder):
        # print(f)
        if f == '.git' or f == '__pycache__' or f == 'build' or f == '.gitignore':
            print('ignore:', f)
            continue
        elif f == 'textures':
            os.makedirs(build_folder + '/src/textures/compressed/', exist_ok=True)
            copytree(project_folder + '/textures/compressed', build_folder + '/src/textures/compressed')
            print('copied folder:', '/textures/compressed')
            size += os.stat(project_folder + '/textures/compressed').st_size
        else:
            file_path = os.path.join(project_folder, f)
            copy(file_path, build_folder + '/src/' + f)
            size += os.stat(file_path).st_size
            print('copied asset:', f)
    return size


def create_bat():
    with open(build_folder + '/run.bat', 'w') as f:
        f.write('''start "" "%CD%\python\pythonw.exe" %CD%\src\main.py''')
    print('created .bat file')


def has_parent_directory(filepath, dirname):
    try:
        parent_folder = os.path.dirname(filepath)
        print('parentfolder:', parent_folder)
        if parent_folder == dirname:
            return True
        else:
            has_parent_directory(parent_folder, dirname)

    except:
        # print('end')
        return False


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            try:
                shutil.copytree(s, d, symlinks, ignore)
            except Exception as e:
                print(e)
        else:
            shutil.copy2(s, d)


if len(sys.argv) == 1:
    print('error: please provide project folder path')
    sys.exit()

if sys.argv[1] == 'help':
    print(
'''package ursina application for windows10.
provided with project folder path, creates a build folder where
it copies python and project's dependent packages. requires a main.py file.
copies game scripts and assets into 'build/scr' folder.
creates a .bat file to start the game.'''
    )
    sys.exit()


project_folder = sys.argv[1]
build_folder = os.path.join(project_folder, 'build')
print('building project:', project_folder)

if not os.path.exists(build_folder):
    os.makedirs(build_folder)
if not os.path.exists(build_folder + '/python/'):
    os.makedirs(build_folder + '/python/')
if not os.path.exists(build_folder + '/python/DLLs'):
    os.makedirs(build_folder + '/python/DLLs')
if not os.path.exists(build_folder + '/python/Lib'):
    os.makedirs(build_folder + '/python/Lib')
if not os.path.exists(build_folder + '/src/'):
    os.makedirs(build_folder + '/src/')

python_folder = (os.path.dirname(sys.executable)).replace('\\', '/')
python_size = copy_python()
python_lib_size = copy_python_lib()
always_included_size = copy_always_included()
ursina_size = copy_ursina()
found_modules_size = copy_found_modules()
assets_size = copy_assets()
create_bat()

print('python size:', size(python_size))
print('python lib size:', size(python_lib_size))
print('always included size:', size(always_included_size))
print('ursina size:', size(ursina_size))
print('found modules size:', size(found_modules_size))
print('assets size:', size(assets_size))
print(
    'TOTAL SIZE:',
    size(
        python_size
        + python_lib_size
        + always_included_size
        + ursina_size
        + found_modules_size
        )
    )
