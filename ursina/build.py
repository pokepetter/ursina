import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from shutil import copy
from textwrap import dedent
import platform as py_platform


from ursina.cmd_tool_maker import auto_log_method_calls, auto_validate_input, make_command_line_app


def ask_to_overwrite(path):
    msg = f'{path} already exists. \nProceed to delete and overwrite?'
    return input(f'{msg} (y/N) ').lower() == 'y'


PROJECT_FOLDER = Path.cwd()
SRC_FOLDER = PROJECT_FOLDER / PROJECT_FOLDER.name

print('SRC_FOLDER:', SRC_FOLDER)

@auto_validate_input
@auto_log_method_calls
class UrsinaBuild:
    # TODO: Need __init__  make_command_line_app to work currently, but remove after that's fixed.
    def __init__(self):
        self.ignore_folders = []
        self.ignore_filetypes = []


    def build(self,
            builds_folder='builds',
            build_name='',
            platform='Windows',
            build_engine=True,
            build_game=True,
            compile_to_pyc=True,
            make_bat_file=True,
            entry_point='main.py',
            overwrite=False,
            pyproject_path='..',
            python_version='',
        ):
        if not (SRC_FOLDER/entry_point).exists():
            raise Exception(f'No {(SRC_FOLDER/entry_point)} found.')

        if isinstance(builds_folder, str):
            builds_folder = PROJECT_FOLDER / builds_folder
        builds_folder.mkdir(exist_ok=True)
        build_name = build_name if build_name else PROJECT_FOLDER.name

        print('building project:', SRC_FOLDER)
        start_time = time.time()

        if build_engine:
            self.build_engine(builds_folder=builds_folder, build_name=build_name, platform=platform, overwrite=overwrite, python_version=python_version)

        if build_game:
            self.build_game(builds_folder=builds_folder, build_name=build_name, platform=platform, overwrite=overwrite, compile_to_pyc=compile_to_pyc)

        if make_bat_file:
            self.make_bat_file(builds_folder=builds_folder, build_name=build_name, platform=platform, entry_point=entry_point, is_pyc=compile_to_pyc)

        print('build complete! time elapsed:', time.time() - start_time)



    def build_engine(self, overwrite=False, builds_folder='builds', build_name='', platform='Windows', python_version=''): # copies python and modules into the 'python' folder
        build_name = build_name if build_name else PROJECT_FOLDER.name
        into = Path(f'{builds_folder}/{build_name}_{platform}/python/')
        into.mkdir(parents=True, exist_ok=True)

        if into.exists():
            shutil.rmtree(str(into))

        if not python_version:
            python_version = py_platform.python_version()
            print(f'No python_version specified, using default: {python_version}')
        self.copy_python(builds_folder=builds_folder, build_name=build_name, platform=platform, python_version=python_version)
        self.copy_modules(builds_folder=builds_folder, build_name=build_name, platform=platform, python_version=python_version)
        return self


    def copy_python(self,
                    builds_folder='builds',
                    build_name='',
                    platform='Windows',
                    python_version='',
                    use_cache=True,
                    cache_dir='build_cache/python_embeds'):
        import shutil
        import urllib.request
        import zipfile

        if not python_version:
            python_version = py_platform.python_version()
            print(f'No python_version specified, using default: {python_version}')

        build_name = build_name if build_name else PROJECT_FOLDER.name
        into = Path(f'{builds_folder}/{build_name}_{platform}/python/')
        into.mkdir(parents=True, exist_ok=True)

        if isinstance(cache_dir, str):
            cache_dir = PROJECT_FOLDER / cache_dir
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_zip = cache_dir / f'python-{python_version}-embed-amd64.zip'

        if use_cache and cache_zip.exists():
            print(f'      Using cached embeddable Python {python_version} at: {cache_zip}')
        else:
            url = f'https://www.python.org/ftp/python/{python_version}/python-{python_version}-embed-amd64.zip'
            print(f'      Downloading Windows embeddable Python {python_version} from: {url} ...')
            urllib.request.urlretrieve(url, cache_zip)
            print('      Downloaded and cached at:', cache_zip)

        # Copy cached file into build directory (optional, but nice separation)
        zip_file = into / 'python-embed.zip'
        if zip_file.exists():
            zip_file.unlink()
        shutil.copy2(cache_zip, zip_file)

        print('      Extracting...')
        with zipfile.ZipFile(zip_file) as zf:
            zf.extractall(into)
        print('      Windows embeddable Python extracted.')

        major, minor, _ = python_version.split('.')
        print('INTO:', into)
        print(major, minor, _)
        pth_file = into / f'python{major}{minor}._pth'
        print('      pth_file:', pth_file)
        # add build folder so it can import the src as package, and import site to load other packages
        with pth_file.open('a') as f:
            f.write('\n..\nimport site\n')

        return self


    def copy_modules(self,
                    builds_folder='builds',
                    build_name='',
                    platform='Windows',
                    cache_dir='build_cache/wheels',
                    platform_tag = 'win_amd64',
                    python_version='',
                    abi='',
                    ):
        build_name = build_name if build_name else PROJECT_FOLDER.name
        into = Path(f'{builds_folder}/{build_name}_{platform}/python/Lib/site-packages/')
        into.mkdir(parents=True, exist_ok=True)

        cache_dir = PROJECT_FOLDER / cache_dir
        cache_dir.mkdir(parents=True, exist_ok=True)
        print('     copy modules to:', into)

        if not python_version:
            python_version = py_platform.python_version()
            print(f'No python_version specified, using default: {python_version}')
        major, minor, patch = python_version.split('.')
        python_major_minor = f'{major}.{minor}'
        if not abi:
            abi = f'cp{major}{minor}'

        # ensure requirements.txt exists
        # if not (PROJECT_FOLDER / 'requirements.txt').exists():
        subprocess.run(['uv', 'pip', 'compile', 'pyproject.toml',
                            '-o', 'requirements.txt'],
                        capture_output=True, text=True)

        with open(PROJECT_FOLDER / 'requirements.txt') as f:
            packages = [line for line in f.read().split('\n')
                        if line and not line.strip().startswith('#')]

        print('packages:', '\n'.join(packages))


        pip_base = [sys.executable, '-m', 'pip', 'download']
        pip_args = [
            '--platform', platform_tag,
            '--python-version', python_major_minor,
            '--implementation', 'cp',
            '--abi', abi,
            '-d', str(cache_dir),  # << store wheels in cache
        ]

        success = []
        fail = []

        # Pass 1 — Try to reuse cache before downloading
        for pkg in packages:
            cached_wheels = list(cache_dir.glob(f'{pkg.replace('-', '_')}*{python_major_minor}*.whl'))
            if cached_wheels:
                print(f'      Using cached wheel for {pkg}')
                success.append(pkg)
                continue

            # detect local path: contains slash or begins with ., .., or /
            if '/' in pkg or pkg.startswith('.'):
                local_path = Path(pkg).resolve()
                if not local_path.is_dir():
                    print(f'Skipping {local_path}, folder not found')
                    continue

                result = subprocess.run(['pip', 'wheel', pkg, '-w', cache_dir])
                if result.returncode == 0:
                    success.append(pkg)
                else:
                    fail.append(pkg)

            print(f'      No cache for {pkg}, trying binary download')
            result = subprocess.run(pip_base + ['--only-binary=:all:'] + pip_args + [pkg])
            if result.returncode == 0:
                success.append(pkg)
            else:
                fail.append(pkg)

        # Pass 2 — fallback to source wheels if binary wasn’t available
        for pkg in fail[:]:
            print(f'      Trying source fallback for {pkg}')
            result = subprocess.run(pip_base + ['--no-binary=:all:'] + pip_args + [pkg])
            if result.returncode == 0:
                success.append(pkg)
                fail.remove(pkg)

        if fail:
            print(f'⚠️ Failed to download: {fail}')
        else:
            print('All packages downloaded successfully.')

        print('Extracting wheels...')

        # Copy from cache → into
        for wheel in cache_dir.glob('*.whl'):
            shutil.copy2(wheel, into / wheel.name)

        # Extract wheels
        for wheel in into.glob('*.whl'):
            with zipfile.ZipFile(wheel, 'r') as z:
                z.extractall(into)   # MUST extract into site-packages
            print(f'Extracted {wheel.name}')
            wheel.unlink()

        print('✅ Module install complete (cached+extracted).')
        return self



    def build_game(self, builds_folder='builds', build_name='', platform='Windows', overwrite=False, compile_to_pyc=True, copy_assets=True):
        build_name = build_name if build_name else PROJECT_FOLDER.name
        into = Path(f'{builds_folder}/{build_name}_{platform}/{PROJECT_FOLDER.name}/')

        if not into.exists():
            overwrite = True
        if into.exists() and not overwrite:
            overwrite = ask_to_overwrite(into)
        if not overwrite:
            return self

        if into.exists():
            shutil.rmtree(str(into))
        into.mkdir(exist_ok=True, parents=True)

        extra_ignore_filetypes = ['.py'] if compile_to_pyc else ['.pyc']

        if copy_assets:
            self.copy_assets(builds_folder=builds_folder, build_name=build_name, platform=platform, extra_ignore_filetypes=extra_ignore_filetypes)

        if compile_to_pyc: # make sur to do this after copying assets since it deletes the folder
            self.compile_to_pyc()

        self.make_bat_file(builds_folder=builds_folder, build_name=build_name, platform=platform, is_pyc=compile_to_pyc)
        return self


    def compile_to_pyc(self, builds_folder='builds', build_name='', platform='Windows', glob_pattern='**//*.py'):
        build_name = build_name if build_name else PROJECT_FOLDER.name
        into = Path(f'{builds_folder}/{build_name}_{platform}/{PROJECT_FOLDER.name}/')

        import py_compile
        for f in SRC_FOLDER.glob(glob_pattern):
            print('maybe copy:', f)
            in_ignore = False
            for e in self.ignore_folders:
                if e in [str(e.name) for e  in f.parents]:
                    in_ignore = True
                    print('skip compiling:', f)
                    break
            if in_ignore:
                continue

            parents = f.relative_to(SRC_FOLDER).parents
            if 'scenes' in parents:
                continue
            py_compile.compile(f, into / f'{f.stem}.pyc')


    def copy_assets(self,
            builds_folder='builds',
            build_name='',
            platform='Windows',
            ignore_folders=['builds', '.venv', 'build.bat','__pycache__','.git'],
            ignore_filetypes=['.gitignore', '.psd', '.zip', '.blend', '.blend1', '.kra', '.kra~'],
            extra_ignore_filetypes=[],
        ):
        ignore_filetypes.extend(extra_ignore_filetypes)

        build_name = build_name if build_name else PROJECT_FOLDER.name
        into = Path(f'{builds_folder}/{build_name}_{platform}/{PROJECT_FOLDER.name}/')
        if into.exists():
            shutil.rmtree(str(into))

        compressed_textures = []
        compressed_textures_folder = Path(SRC_FOLDER / 'textures_compressed')
        if compressed_textures_folder.exists():
            compressed_textures = list(compressed_textures_folder.glob('**/*.*'))
            compressed_textures = [f.stem for f in compressed_textures if f.suffix not in ignore_filetypes]

        compressed_models = []
        compressed_models_folder = Path(SRC_FOLDER / 'models_compressed')
        if compressed_models_folder.exists():
            compressed_models = list(compressed_models_folder.glob('**/*.bam'))
            compressed_models = [f.stem for f in compressed_models if f.suffix not in ignore_filetypes]


        for f in SRC_FOLDER.rglob('*'):
            if f.is_dir():
                continue  # folder creation happens implicitly via mkdir

            rel = f.relative_to(SRC_FOLDER)

            # folder ignore rule
            if any(ign in rel.parts for ign in ignore_folders):
                print(f'ignore folder rule: {rel}')
                continue

            # extension ignore rule
            if f.suffix in ignore_filetypes:
                print(f'ignore filetype: {rel}')
                continue

            if f.stem in compressed_textures and f.parent != compressed_textures_folder:
                continue
            # print(f.name, f.parent, f.stem in compressed_models)
            if f.stem in compressed_models and f.parent != compressed_models_folder:
                continue

            dest = into / rel
            dest.parent.mkdir(parents=True, exist_ok=True)

            print('copy:', rel, '->', dest)
            shutil.copy2(f, dest)


    def make_bat_file(self, entry_point='main.py', name='launch', builds_folder='builds', build_name='', platform='Windows', is_pyc=False):
        build_name = build_name if build_name else PROJECT_FOLDER.name
        into = Path(f'{builds_folder}/{build_name}_{platform}/')

        c = 'c' if is_pyc else ''
        # launch_debug, with output to log.txt
        with (Path(into) / f'{name}_debug.bat').open('w') as f:
            f.write(dedent(fr'''
                chcp 65001
                set PYTHONIOENCODING=utf-8

                pushd "{PROJECT_FOLDER.name}"
                call "..\python\python.exe" "{entry_point}{c}" > "..\log.txt" 2>&1
                popd
                '''
            ))

        with (Path(into) / f'{name}.bat').open('w') as f:
            f.write(dedent(fr'''
                chcp 65001å
                set PYTHONIOENCODING=utf-8

                pushd "{PROJECT_FOLDER.name}"
                call "..\python\pythonw.exe" "{entry_point}{c}"
                popd
                '''
            ))
        return self

    # make exe
    # import subprocess
    # import importlib
    # spec = importlib.util.find_spec('ursina')
    # ursina_path = Path(spec.origin).parent
    # subprocess.call([
    #     f'{ursina_path}\\scripts\\_bat_to_exe.bat',
    #     f'{build_folder}\\{project_name}.bat',
    #     f'\\build\\{PROJECT_FOLDER.stem}.exe'
    #     ])


if __name__ == '__main__':
    make_command_line_app(UrsinaBuild)