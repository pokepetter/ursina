from setuptools import find_packages, setup

setup(
    name='pandaeditor',
    version='0.1',
    url='https://github.com/pokepetter/pandaeditor',
    author='Petter Amland',
    author_email='pokepetter@gmail.com',
    license='MIT',
    keywords='game development',
    packages=find_packages(),
    # packages=find_packages(['']),cmd
    requires=['panda3d', ]
    )
