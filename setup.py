from setuptools import find_packages, setup

setup(
    name='ursina',
    version='0.2',
    url='https://github.com/pokepetter/ursina',
    author='Petter Amland',
    author_email='pokepetter@gmail.com',
    license='MIT',
    keywords='game development',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'panda3d',
        'pillow',
        'screeninfo',
    ],

    extras_require={
        'extras':  ['psd-tools', 'imageio', 'psutil', 'hurry.filesize'],
    }
)
