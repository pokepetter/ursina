# ursina    ʕ •ᴥ•ʔゝ□

[Website](https://pokepetter.github.io/ursina/index.html) | [Discord](https://discord.gg/ydXfhyb) | [Twitter](https://twitter.com/ursinaengine) | [Patreon](https://www.patreon.com/ursinaengine) | [Sponsor](https://github.com/sponsors/pokepetter)

An easy to use game engine/framework for python.

![Banner](/docs/made_with_ursina.jpg)

[![Trailer](/docs/ursina_trailer_preview.webp)](https://youtu.be/j71j88oCTNo)

## Getting Started
1) Install [Python 3.10 or newer.](https://www.python.org/downloads/release/python-3100)

2) Open cmd/terminal and type:

```
pip install ursina
```


To get the newest, in development version from GitHub, install it like this:

```
pip install git+https://github.com/pokepetter/ursina.git
```


If you want to easily edit the source, it's recommended to clone the git
repo and pip install with --editable flag like this. Make sure you have [git](https://git-scm.com) installed.

```
git clone https://github.com/pokepetter/ursina.git
cd ursina
pip install --editable .
```


Also install any of the optional dependencies you want from the list below,
or install them all with:

```
pip install ursina[extras]
```


On some systems you might have to use pip3 instead of pip in order to use Python 3 and not the old Python 2.
To use a specific Python version, use:
```
python3.xx -m pip install ursina
```
Where 3.xx is the version you want to target.


## Dependencies
  * python 3.10+
  * panda3d
  * pillow, for texture manipulation
  * psd-tools, for converting .psd files
  * blender, for converting .blend files
  * pyperclip, for copy/pasting


## Examples
``` python
from ursina import *            # this will import everything we need from ursina with just one line.

app = Ursina()
ground = Entity(
    model = 'cube',
    color = color.magenta,
    z = -.1,
    y = -3,
    origin = (0, .5),
    scale = (50, 1, 10),
    collider = 'box',
    )

app.run()                       # opens a window and starts the game.
```


* [Minecraft Clone](https://pokepetter.github.io/ursina/minecraft_clone.html)

* [Platformer Game](https://pokepetter.github.io/ursina/platformer.html)

There are other examples in [the samples folder](https://github.com/pokepetter/ursina/tree/master/samples), or in [samples website](https://pokepetter.github.io/ursina/samples.html)

## How do I make a game?
Ursina games are made by writing Python code. You can use any text editor you want, but personally I like to use Atom.
1) Create an empty .py file called `ursina_game.py`
2) Copy this text into your new file:
``` python
from ursina import *           # this will import everything we need from ursina with just one line.

app = Ursina()

player = Entity(
    model = 'cube' ,           # finds a 3d model by name
    color = color.orange,
    scale_y = 2
    )

def update():                  # update gets automatically called by the engine.
    player.x += held_keys['d'] * .1
    player.x -= held_keys['a'] * .1


app.run()                     # opens a window and starts the game.
```

3) Run this in the terminal start the game:

       python ursina_game.py
   
   ... or run it with your editor/IDE of choice.

4) You can now move the orange box around with 'a' and 'd'!

   To close the window, you can by default, press control+shift+alt+q or press the red x.

## Documentation
   * [Ursina Documentation](https://pokepetter.github.io/ursina/documentation.html)
      - Written explanations of core concepts and how Ursina works.
   * [Ursina API Reference](https://pokepetter.github.io/ursina/api_reference.html)
      - List of Ursina's functions, classes and assets.
   * [Samples](https://pokepetter.github.io/ursina/samples.html)
      - Small example games.

Found a bug? Posting it in [Issues](https://github.com/pokepetter/ursina/issues).
Fixed a bug? Make a [pull request](https://github.com/pokepetter/ursina/pulls).


## Project Structure
```
## Project Structure

📁docs
    📃index.txt
    📃documentation.txt
    📃inventory_tutorial.txt
    ...
        # text files for the website. gets turned into .html files with sswg.

    📃cheat_sheet.html
        # auto generated documentation made with documentation_generator.py.

    📃tutorial_generator.py
        # turns specific .py files into .txt files, which can then be turned into .html by sswg.
        # this extracts the comments from the source files into description for that step and the code after into code blocks.
        # see platformer_tutorial.py for an example.

📁samples               # small example games.

📁ursina                # the actual ursina module.
    📁audio                 # built-in audio clips.
    📁editor                # the 3d level editor for ursina.
    📁fonts                 # built-in fonts.
    📁models                # .blend files, source files, for built-in 3d models.
        📁procedural            # classes for generating 3d models, like Cylinder, Quad and Terrain.
    📁models_compressed     # .blend files converted to .ursinamesh.
    📁prefabs               # higher level classes like Draggable, Slider, Sprite, etc.

    📃__init__.py
    📃application.py
    📃audio.py
    ...
        # ursina base modules, like code for Entity, input_handler, Text, window and so on.

```
