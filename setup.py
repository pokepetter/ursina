from setuptools import find_packages, setup

with open("README.md", encoding="UTF-8") as f:
    long_desc = f.read()

setup(
    name='ursina',
    description='An easy to use game engine/framework for python.',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    version='4.1.1',
    url='https://github.com/pokepetter/ursina',
    author='Petter Amland',
    author_email='pokepetter@gmail.com',
    license='MIT',
    keywords='game development',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'panda3d',
        'panda3d-gltf',
        'pillow',
        'pyperclip',
    ],
    extras_require={'extras': [
        'numpy',
        'imageio',
        'psd-tools3',
        'psutil',
        ],
    },
    python_requires='>=3.6',
)
