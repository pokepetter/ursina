from modulefinder import ModuleFinder
import os
import sys
import shutil
from shutil import copy, copyfile
from distutils.dir_util import copy_tree
from pathlib import Path
import time
from textwrap import dedent

project_folder = Path.cwd()
project_name = project_folder.stem
build_folder = Path(project_folder / 'build')
build_folder.mkdir(exist_ok=True)

ignore = []

compressed_textures = []
compressed_textures_folder = Path(project_folder/'textures_compressed')
if compressed_textures_folder.exists():
    compressed_textures = compressed_textures_folder.iterdir()

def copytree(src, dst, symlinks=False, ignore_filetypes=[]):
    src = str(src)
    dst = str(dst)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            try:
                ignore_pattern = shutil.ignore_patterns(*ignore_filetypes)
                shutil.copytree(s, d, symlinks, ignore_pattern)
            except Exception as e:
                print(e)
        else:
            if Path(s).suffix in ignore_filetypes:
                print('ignore:', Path(s).suffix)
                continue
            if Path(s).stem in compressed_textures:
                continue
            shutil.copy2(s, d)






include_modules = []

python_dest = Path(build_folder / 'python')
python_dlls_dest = Path(build_folder / 'python/DLLs')
python_lib_dest = Path(build_folder / 'python/Lib')
src_dest = Path(build_folder / 'src')
build_engine = True
build_game = True
compile_to_pyc = True

for i, arg in enumerate(sys.argv):
    if arg == '--help':
        print(dedent('''
            package ursina application for windows10.
            provided with project folder path, creates a build folder where
            it copies python and project's dependent packages. requires a main.py file.
            copies game scripts and assets into 'build/src' folder.
            creates a .bat file to start the game.
            include extra modules like this: --include_modules module_one,module_two,module_tree
            --ignore            # add assets to ignore
            --name              # change project name
            --include_modules   # include extra modules
            --overwrite         # don't ask to overwrite existing build, just overwrite
            --skip_engine
            --skip_game
            --compile_to_pyc    # default: True

            Make sure to include any extra modules with --include_modules PIL,numpy for example.
            Any errors while the application is running will be logged in log.txt instead of the console.
            '''
            )
        )
        sys.exit()

    elif arg == '--ignore':
        for j in range(i, len(sys.argv)):
            if sys.argv[j].startswith('-'):
                break
            ignore.append(sys.argv[j])
            print('ignoring', sys.argv[j])

    elif arg == '--name':
        project_name = sys.argv[i+1]

    elif arg == '--include_modules':
        include_modules = sys.argv[i+1].split(',')

    elif arg == '--skip_engine':
        build_engine = False
    elif arg == '--skip_game':
        build_game = False

    elif arg == '--compile_to_pyc':
        compile_to_pyc = bool(sys.argv[i+1])


if (build_engine and python_dest.exists() or (build_game and src_dest.exists())):
    if not '--overwrite' in sys.argv:
        for e in (python_dest, src_dest):
            msg = f'Folder {e} already exists. \nProceed to delete and overwrite?'
            overwrite = input("%s (y/N) " % msg).lower() == 'y'
            # if not overwrite:
            #     print('stopped building')
            #     exit()
            if e == python_dest:
                build_engine = overwrite
            elif e == src_dest:
                build_game = overwrite


print('building project:', project_folder)
start_time = time.time()

if build_engine:
    if python_dest.exists():
        shutil.rmtree(str(python_dest))
    python_dest.mkdir()
    python_dlls_dest.mkdir()
    python_lib_dest.mkdir()


    # def copy_python():
    # copy files in python installation folder, but not the folders
    print('copying python')
    python_folder = Path(sys.executable).parent
    [copy(str(f), str(python_dest / f.name)) for f in python_folder.iterdir() if f.is_file()]


    # def copy_python_lib():
    print('copying python Lib files')
    [copy(str(f), str(python_lib_dest / f.name)) for f in Path(python_folder / 'Lib').iterdir() if f.is_file()]


    # def copy_always_included():
    print('copying always included modules and extra modules')
    include_modules = [f'Lib/site-packages/{e}' for e in include_modules]

    always_include = [
        'Lib/collections',
        'Lib/ctypes',
        'Lib/encodings',
        'Lib/importlib',
        'Lib/urllib',
        'Lib/logging',
        'Lib/xml',
        # 'Lib/site-packages/panda3d/',
        'Lib/site-packages/direct/',
        'Lib/site-packages/pyperclip/',
        'Lib/site-packages/PIL/',
        'DLLs/libffi-7.dll',
        'DLLs/_ctypes.pyd',
        ]

    for path in always_include + include_modules:
        source = python_folder / path
        dest = python_dest / path
        print('copying always include:', source, '-->', dest)

        if source.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            copy(str(source), str(dest))
        elif source.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            copytree(source, dest)


    print('copying panda3d')
    (python_dest / 'Lib/site-packages/panda3d/').mkdir(parents=True, exist_ok=True)

    for f in (python_folder / 'Lib/site-packages/panda3d/').iterdir():
        if f.name in (
            'avcodec-55.dll',
            'fmodex64.dll',
            'egg.cp39-win_amd64.pyd',
            'libpandaode.dll',
            'ode.cp39-win_amd64.pyd',
            'models'
            ):
            continue
        print('copying:', f, '-->', str(python_dest / 'Lib/site-packages/panda3d/' / f.name))
        if f.is_file():
            copy(str(f), str(python_dest / 'Lib/site-packages/panda3d/' / f.name))
        else:
            (python_dest / 'Lib/site-packages/panda3d/' / f.name).mkdir(parents=True, exist_ok=True)
            copytree(f, (python_dest / 'Lib/site-packages/panda3d/' / f.name))

    # def copy_ursina():
    print('copying ursina')
    import importlib
    spec = importlib.util.find_spec('ursina')
    ursina_path = Path(spec.origin).parent
    dest = build_folder / 'python/Lib/site-packages/ursina'
    dest.mkdir(parents=True, exist_ok=True)
    copytree(ursina_path, dest, ignore_filetypes=('samples', 'unused'))


    # print('copying found modules')
    # finder = ModuleFinder()
    # finder.run_script(str(project_folder) + '/main.py')

    # for name, mod in finder.modules.items():
    #     filename = mod.__file__
    #
    #     if filename is None:
    #         continue
    #     if '__' in name:
    #         print('ignore:', filename)
    #         continue
    #
    #     if 'Python' in filename and 'DLLs' in filename:
    #         print('copying:', filename)
    #         copy(filename, str(build_folder / 'python/DLLs'))
    #
    #     elif 'lib\\site-packages\\' in filename:
    #         print('copying module:', filename)
    #         forward_slashed = filename.split('lib\\site-packages\\')[1].replace('\\', '/')
    #         dir = build_folder / 'python/lib/site-packages' / forward_slashed
    #         dir.parent.mkdir(parents=True, exist_ok=True)
    #         copy(filename, dir)



if build_game:
    if src_dest.exists():
        shutil.rmtree(str(src_dest))
    src_dest.mkdir()

    ignore.extend(['.git', 'build', '.gitignore', 'build.bat'])
    ignore_patterns = ['.psd', '.zip']
    ignore.append('__pycache__')

    if compile_to_pyc:
        import py_compile
        for f in project_folder.glob('**/*.py'):
            if '\\build\\' in str(f):
                continue

            print('compiling:', f, src_dest / str(f)[len(str(project_folder))+1:])
            py_compile.compile(f, src_dest / (str(f)[len(str(project_folder))+1:]+'c'))

        ignore_patterns.append('.py')


    print('copying assets')
    for f in project_folder.iterdir():
        name = f.name
        dest = Path(src_dest / f.name)
        if name in ignore:
            print('ignore:', f)
            continue
        elif f.is_dir():
            print('copying assetfolder:', f, 'to', dest)
            dest.mkdir(parents=True, exist_ok=True)
            copytree(project_folder / f, dest, ignore_filetypes=ignore_patterns)
        elif f.is_file():
            if f.suffix in ignore_patterns:
                continue
            print('copying asset:', f, 'to', src_dest / f.name)
            copy(str(f), str(dest))


    print('creating .bat file')
    c = ''
    if compile:
        c = 'c'
    with Path(build_folder / f'{project_name}.bat').open('w') as f:
        f.write(dedent(fr'''
            chcp 65001
            set PYTHONIOENCODING=utf-8

            call "python\python.exe" "src\main.py{c}" > "log.txt" 2>&1'''
        ))

# make exe
# import subprocess
# import importlib
# spec = importlib.util.find_spec('ursina')
# ursina_path = Path(spec.origin).parent
# subprocess.call([
#     f'{ursina_path}\\scripts\\_bat_to_exe.bat',
#     f'{build_folder}\\{project_name}.bat',
#     f'\\build\\{project_folder.stem}.exe'
#     ])


print('build complete! time elapsed:', time.time() - start_time)
