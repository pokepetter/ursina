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
    return input(f"{msg} (y/N) ").lower() == 'y'


def copytree(src, dst, symlinks=False, ignore_patterns=None, ignore_filetypes=None):
    src = Path(src)
    dst = Path(dst)
    ignore_patterns = ignore_patterns if ignore_patterns is not None else []
    ignore_filetypes = ignore_filetypes if ignore_filetypes is not None else []

    for item in src.iterdir():
        if item.name in ignore_patterns:
            continue

        dest_item = dst / item.name

        if item.is_dir():
            try:
                ignore_pattern = shutil.ignore_patterns(*(ignore_patterns + [f'*{e}' for e in ignore_filetypes]))
                shutil.copytree(item, dest_item, symlinks=symlinks, ignore=ignore_pattern)
            except Exception as e:
                print(e)
        else:
            if item.suffix in ignore_filetypes:
                print('ignore filetype:', item.suffix)
                continue
            # if item.stem in self.compressed_textures:
            #     continue
            shutil.copy2(item, dest_item)

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
            output_folder='builds',
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

        project_name = PROJECT_FOLDER.stem
        if isinstance(output_folder, str):
            output_folder = PROJECT_FOLDER / output_folder
        output_folder.mkdir(exist_ok=True)
        self.build_folder = Path(output_folder / f'build_{platform}_v{'x_x_x'}')
        self.build_folder.mkdir(exist_ok=True)

        print('building project:', SRC_FOLDER)
        start_time = time.time()

        if build_engine:
            self.build_engine(overwrite=overwrite, python_version=python_version)

        if build_game:
            self.build_game(overwrite=overwrite, compile_to_pyc=compile_to_pyc)

        if make_bat_file:
            self.make_bat_file(entry_point=entry_point, is_pyc=compile_to_pyc)

        print('build complete! time elapsed:', time.time() - start_time)



    def build_engine(self, overwrite=False, into='builds/_test_build/python', python_version=''):
        into = (PROJECT_FOLDER / into)
        into.mkdir(parents=True, exist_ok=True)

        # python_dest = self.build_folder / 'python'
        # python_dlls_dest = self.build_folder / 'python/DLLs'
        # python_lib_dest = self.build_folder / 'python/Lib'

        # if python_dest.exists() and not overwrite:
        #     overwrite = ask_to_overwrite()
        # if not overwrite:
        #     return self

        if into.exists():
            shutil.rmtree(str(into))
        # python_dest.mkdir()
        # python_dlls_dest.mkdir()
        # python_lib_dest.mkdir()

        if not python_version:
            python_version = py_platform.python_version()
            print(f'No python_version specified, using default: {python_version}')
        self.copy_python(into=into, python_version=python_version)
        self.copy_modules(into=into/'Lib/site-packages', python_version=python_version)

        return self



    def copy_python(self, python_version='', platform='Windows',
                    into='builds/_test_build/python/',
                    use_cache=True,
                    cache_dir='build_cache/python_embeds'):
        import shutil
        import urllib.request
        import zipfile

        if not python_version:
            python_version = py_platform.python_version()
            print(f'No python_version specified, using default: {python_version}')

        # Resolve target dir
        if isinstance(into, str):
            into = PROJECT_FOLDER / into
        into.mkdir(parents=True, exist_ok=True)

        # Resolve cache dir
        if isinstance(cache_dir, str):
            cache_dir = PROJECT_FOLDER / cache_dir
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Cache file path (per Python version)
        cache_zip = cache_dir / f"python-{python_version}-embed-amd64.zip"

        # If cached, reuse it; otherwise download and cache
        if use_cache and cache_zip.exists():
            print(f"      Using cached embeddable Python {python_version} at: {cache_zip}")
        else:
            url = f"https://www.python.org/ftp/python/{python_version}/python-{python_version}-embed-amd64.zip"
            print(f"      Downloading Windows embeddable Python {python_version} from: {url} ...")
            urllib.request.urlretrieve(url, cache_zip)
            print("      Downloaded and cached at:", cache_zip)

        # Copy cached file into build directory (optional, but nice separation)
        zip_file = into / "python-embed.zip"
        if zip_file.exists():
            zip_file.unlink()
        shutil.copy2(cache_zip, zip_file)

        print("      Extracting...")
        with zipfile.ZipFile(zip_file) as zf:
            zf.extractall(into)
        print("      Windows embeddable Python extracted.")

        major, minor, _ = python_version.split('.')
        print('INTO:', into)
        print(major, minor, _)
        pth_file = into / f'python{major}{minor}._pth'
        print('      pth_file:', pth_file)
        # add build folder so it can import the src as package, and import site to load other packages
        with pth_file.open('a') as f:
            f.write('\n..\nimport site\n')

        return self

            # copy files in python installation folder, but not the folders
            # python_folder = Path(sys.executable).parent
            # [copy(str(f), str(python_dest / f.name)) for f in python_folder.iterdir() if f.is_file()]


    def copy_modules(self,
                    into='builds/_test_build/python/Lib/site-packages/',
                    cache_dir="build_cache/wheels",
                    platform_tag = "win_amd64",
                    python_version='',
                    abi='',
                    ):

        if isinstance(into, str):
            into = Path(into)
        into.mkdir(parents=True, exist_ok=True)

        cache_dir = PROJECT_FOLDER / cache_dir
        cache_dir.mkdir(parents=True, exist_ok=True)
        print("     copy modules to:", into)

        if not python_version:
            python_version = py_platform.python_version()
            print(f'No python_version specified, using default: {python_version}')
        major, minor, patch = python_version.split('.')
        python_major_minor = f'{major}.{minor}'
        if not abi:
            abi = f'cp{major}{minor}'

        # ensure requirements.txt exists
        # if not (PROJECT_FOLDER / "requirements.txt").exists():
        subprocess.run(["uv", "pip", "compile", "pyproject.toml",
                            "-o", "requirements.txt"],
                        capture_output=True, text=True)

        with open(PROJECT_FOLDER / "requirements.txt") as f:
            packages = [line for line in f.read().split("\n")
                        if line and not line.strip().startswith('#')]

        print("packages:", "\n".join(packages))

        pip_base = [sys.executable, "-m", "pip", "download"]
        pip_args = [
            "--platform", platform_tag,
            "--python-version", python_major_minor,
            "--implementation", "cp",
            "--abi", abi,
            "-d", str(cache_dir),  # << store wheels in cache
        ]

        success = []
        fail = []

        # Pass 1 — Try to reuse cache before downloading
        for pkg in packages:
            cached_wheels = list(cache_dir.glob(f"{pkg.replace('-', '_')}*{python_major_minor}*.whl"))
            if cached_wheels:
                print(f"      Using cached wheel for {pkg}")
                success.append(pkg)
                continue

            print(f"      No cache for {pkg}, trying binary download")
            result = subprocess.run(pip_base + ["--only-binary=:all:"] + pip_args + [pkg])
            if result.returncode == 0:
                success.append(pkg)
            else:
                fail.append(pkg)

        # Pass 2 — fallback to source wheels if binary wasn’t available
        for pkg in fail[:]:
            print(f"      Trying source fallback for {pkg}")
            result = subprocess.run(pip_base + ["--no-binary=:all:"] + pip_args + [pkg])
            if result.returncode == 0:
                success.append(pkg)
                fail.remove(pkg)

        if fail:
            print(f"⚠️ Failed to download: {fail}")
        else:
            print("All packages downloaded successfully.")

        print("Extracting wheels...")

        # Copy from cache → into
        for wheel in cache_dir.glob("*.whl"):
            shutil.copy2(wheel, into / wheel.name)

        # Extract wheels
        for wheel in into.glob("*.whl"):
            with zipfile.ZipFile(wheel, 'r') as z:
                z.extractall(into)   # MUST extract into site-packages
            print(f"Extracted {wheel.name}")
            wheel.unlink()

        print("✅ Module install complete (cached+extracted).")
        return self



    def build_game(self, into='', overwrite=False, compile_to_pyc=False, copy_assets=True):
        if not into:
            into = Path(f'builds/_test_build/{PROJECT_FOLDER.name}/')

        if isinstance(into, str):
            into = Path(into)

        if not into.exists():
            overwrite = True
        if into.exists() and not overwrite:
            overwrite = ask_to_overwrite(into)
        if not overwrite:
            return self

        if into.exists():
            shutil.rmtree(str(into))
        into.mkdir(exist_ok=True)

        # self.ignore_folders.extend(['build_Windows', 'build_Linux', 'build.bat', '__pycache__', '.git'])
        # self.ignore_filetypes.extend(['.gitignore', '.psd', '.zip'])

        ignore_filetypes=['.gitignore', '.psd', '.zip']
        if compile_to_pyc:
            self.compile_to_pyc()
            ignore_filetypes.append('.py')

        if copy_assets:
            self.copy_assets(into=into, ignore_filetypes=ignore_filetypes)

        self.make_bat_file(is_pyc=compile_to_pyc)
        return self


    def compile_to_pyc(self, into='builds/_test_build/src/', glob_pattern='**//*.py'):
        if isinstance(into, str):
            into = PROJECT_FOLDER / into

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
            ignore_folders=['builds', '.venv', 'build_Windows','build_Linux','build.bat','__pycache__','.git'],
            ignore_filetypes=['.gitignore', '.psd', '.zip'],
            into='builds/_test_build/src/',
        ):

        compressed_textures = []
        compressed_textures_folder = Path(SRC_FOLDER / 'textures_compressed')
        if compressed_textures_folder.exists():
            compressed_textures = list(compressed_textures_folder.glob('**/*.*'))
            compressed_textures = [f for f in compressed_textures if f.suffix not in ignore_filetypes]


        for f in SRC_FOLDER.rglob('*'):
            if f.is_dir():
                continue  # folder creation happens implicitly via mkdir

            rel = f.relative_to(SRC_FOLDER)

            # folder ignore rule
            if any(ign in rel.parts for ign in ignore_folders):
                print(f"ignore folder rule: {rel}")
                continue

            # extension ignore rule
            if f.suffix in ignore_filetypes:
                print(f"ignore filetype: {rel}")
                continue

            dest = into / rel
            dest.parent.mkdir(parents=True, exist_ok=True)

            print("copy:", rel, "->", dest)
            shutil.copy2(f, dest)


    def make_bat_file(self, entry_point='main.py', name='launch.bat', into='builds/_test_build/', is_pyc=False):
        c = 'c' if is_pyc else ''
        with (Path(into) / name).open('w') as f:
            f.write(dedent(fr'''
                chcp 65001
                set PYTHONIOENCODING=utf-8

                call "python\python.exe" "{PROJECT_FOLDER.name}\{entry_point}{c}" > "log.txt" 2>&1'''
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