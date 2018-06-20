from setuptools import find_packages, setup

setup(
    name='ursina',
    version='0.1',
    url='https://github.com/pokepetter/ursina',
    author='Petter Amland',
    author_email='pokepetter@gmail.com',
    license='MIT',
    keywords='game development',
    packages=find_packages(),
    include_package_data=True,
    # packages=find_packages(['']),cmd
    requires=['panda3d', ]
    )
