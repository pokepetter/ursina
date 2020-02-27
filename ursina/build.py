from modulefinder import ModuleFinder
import os
import sys
import shutil
from shutil import copy, copyfile
from distutils.dir_util import copy_tree
from pathlib import Path
import time


def copytree(src, dst, symlinks=False, ignore=None):
    src = str(src)
    dst = str(dst)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            try:
                shutil.copytree(s, d, symlinks, ignore)
            except Exception as e:
                print(e)
        else:
            if s.endswith('.psd'):
                continue
            shutil.copy2(s, d)


if len(sys.argv) > 1:
    if sys.argv[1] == 'help' or sys.argv[1] == '--help':
        print(
            '''package ursina application for windows10.
            provided with project folder path, creates a build folder where
            it copies python and project's dependent packages. requires a main.py file.
            copies game scripts and assets into 'build/scr' folder.
            creates a .bat file to start the game.'''
        )
        sys.exit()

ignore = list()
for i, arg in enumerate(sys.argv):
    if arg == '--ignore':
        for j in range(i, len(sys.argv)):
            ignore.append(sys.argv[j])
            print('ignoring', sys.argv[j])
        break

if len(sys.argv) > 1:
    project_folder = Path(sys.argv[1])
else:
    project_folder = Path.cwd()


build_folder = Path(project_folder / 'build')
if build_folder.exists():
    msg = f'Build folder {build_folder} already exists. \nProceed to delete and overwrite?'
    overwrite = input("%s (y/N) " % msg).lower() == 'y'
    if not overwrite:
        print('stopped building')
        exit()

    print('deleting existing build folder')
    shutil.rmtree(str(build_folder))

print('building project:', project_folder)
start_time = time.time()

python_dest = Path(build_folder / 'python')
python_dlls_dest = Path(build_folder / 'python/DLLs')
python_lib_dest = Path(build_folder / 'python/Lib')
src_dest = Path(build_folder / 'src')

build_folder.mkdir()
python_dest.mkdir()
python_dlls_dest.mkdir()
python_lib_dest.mkdir()
src_dest.mkdir()

# def copy_python():
# copy files in python installation folder, but not the folders
print('copying python')
python_folder = Path(sys.executable).parent
[copy(str(f), str(python_dest / f.name)) for f in python_folder.iterdir() if f.is_file()]


# def copy_python_lib():
print('copying python Lib files')
[copy(str(f), str(python_lib_dest / f.name)) for f in Path(python_folder / 'Lib').iterdir() if f.is_file()]


# def copy_always_included():
print('copying always included')
always_include = (
    'Lib/collections', 'Lib/ctypes', 'Lib/encodings',
    'Lib/importlib', 'Lib/urllib', 'Lib/logging',
    'Lib/site-packages/panda3d/',
    )

for path in always_include:
    source = python_folder / path
    dest = python_dest / path
    print('copying:', source)

    if source.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        copy(str(source), str(dest))
    elif source.is_dir():
        dest.mkdir(parents=True, exist_ok=True)
        copytree(source, dest)

# def copy_ursina():
print('copying ursina')
import importlib
spec = importlib.util.find_spec('ursina')
ursina_path = Path(spec.origin).parent
dest = build_folder / 'python/Lib/site-packages/ursina'
dest.mkdir(parents=True, exist_ok=True)
copytree(ursina_path, dest)


print('copying found modules')
finder = ModuleFinder()
finder.run_script(str(project_folder) + '/main.py')

for name, mod in finder.modules.items():
    filename = mod.__file__

    if filename is None:
        continue
    if '__' in name:
        print('ignore:', filename)
        continue

    if 'Python' in filename and 'DLLs' in filename:
        print('copying:', filename)
        copy(filename, str(build_folder / 'python/DLLs'))

    elif 'lib\\site-packages\\' in filename:
        print('copying:', filename)
        forward_slashed = filename.split('lib\\site-packages\\')[1].replace('\\', '/')
        dir = build_folder / 'python/lib/site-packages' / forward_slashed
        dir.parent.mkdir(parents=True, exist_ok=True)
        copy(filename, dir)


print('copying assets')
for f in project_folder.iterdir():
    name = f.name
    dest = Path(src_dest / f.name)
    if name in ['.git', '__pycache__', 'build', '.gitignore'] + ignore:
        print('ignore:', f)
        continue
    elif f.is_dir():
        print('copying assetfolder:', f, 'to', dest)
        dest.mkdir(parents=True, exist_ok=True)
        copytree(project_folder / f, dest, ignore=shutil.ignore_patterns('*psd'))
    elif f.is_file():
        print('copying asset:', f, 'to', src_dest / f.name)
        copy(str(f), str(dest))


print('creating .exe file')
with Path(build_folder / 'run.bat').open('w') as f:
    f.write('''start "" "%CD%\python\python.exe" %CD%\src\main.py''')

import subprocess
subprocess.call([
    f'{ursina_path}\\scripts\\_bat_to_exe.bat',
    f'{build_folder}\\run.bat',
    f'\\build\\{project_folder.stem}.exe'
    ])

os.remove(Path(build_folder / 'run.bat'))

print('build complete! time elapsed:', time.time() - start_time)
