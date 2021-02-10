from setuptools import find_packages, setup

with open("README.md", "r", encoding="UTF-8") as f:
    long_desc = f.read()

setup(
    name='ursina',
    description='An easy to use game engine/framework for python.',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    version='3.4.0',
    url='https://github.com/pokepetter/ursina',
    author='Petter Amland',
    author_email='pokepetter@gmail.com',
    license='MIT',
    keywords='game development',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy',
        'panda3d',
        'pillow',
        'screeninfo',
        'pyperclip',
    ],

    extras_require={
        'extras':  ['psd-tools3', 'imageio', 'psutil', 'hurry.filesize'],
    }
)
