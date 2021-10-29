# ursina    ʕ •ᴥ•ʔゝ□
An easy to use game engine/framework for python.

![Banner](/docs/made_with_ursina.jpg)


## Getting Started
1) Install Python 3.6 or newer. https://www.python.org/downloads/
2) Open cmd/terminal and type:

```
pip install ursina
```


If you want to install the newest version from git, you can install like this:

```
pip install git+https://github.com/pokepetter/ursina.git
```


If you want to easily edit the source, it's recommended to clone the git
repo and install as develop like this. Make sure you have git installed. https://git-scm.com/

```
git clone https://github.com/pokepetter/ursina.git
python setup.py develop
```


Also install any of the optional dependencies you want from the list below,
or install them all with:

```
pip install ursina[extras]
```


On some systems you might have to use pip3 instead of pip in order to use Python 3 and not the old Python 2.


## Dependencies
  * python 3.6+
  * panda3d
  * screeninfo, for detecting screen resolution
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


* [Minecraft Clone](/samples/minecraft_clone.py)

* [Platformer Game](/samples/platformer.py)


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

3) Type this in the terminal to start the game:

       python ursina_game.py
   If you use Atom, I recommend installing the package atom-python-run to run your scripts with the press of a button.

4) You can now move the orange box around with 'a' and 'd'!

   To close the window, you can by default, press shift+q or press the red x. to disable this, write `window.exit_button.enabled = False` somewhere in your code.


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
