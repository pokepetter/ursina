<h1 align="center">ʕ •ᴥ•ʔ</br>ursina</h1>

<p align="center">An easy to use game engine/framework for python.</p>
<hr>

[Banner](https://github.com/tannnxr/ursina/blob/master/docs/made_with_ursina.jpg)


## Introduction

Thank you for choosing ursina.  Our team of developers work hard to create an intuitive game framework.  We appreciate you using and/or contributing to this project. Please open an issue, or create a pull request to start contributing.

## Initial Setup

1. Ensure that you have Python 3.6 or a later version installed. If not, please download it from the official Python website: https://www.python.org/downloads/

2. Open your command prompt or terminal and enter the following command to install Ursina:

```bash
pip install ursina
```

If you wish to install the most recent version of Ursina directly from the GitHub repository, use the following command:

```bash
pip install git+https://github.com/pokepetter/ursina.git
```

In case you need to modify the source code directly, it is advisable to clone the GitHub repository and install it as a development version. Please ensure that Git is installed on your system. You can download Git from: https://git-scm.com/

Execute the following commands:

```bash
git clone https://github.com/pokepetter/ursina.git
python setup.py develop
```

You may also choose to install any of the optional dependencies listed in the next section. Alternatively, you can install all optional dependencies by executing the following command:

```bash
pip install ursina[extras]
```

Note: Some systems might require using `pip3` instead of `pip` to ensure you are using Python 3 and not Python 2.

## Dependencies

The Ursina package relies on the following dependencies:

  * Python 3.6 or later
  * Panda3D
  * Pillow for texture manipulation
  * PSD-Tools for converting .psd files
  * Blender for converting .blend files
  * Pyperclip for copy/pasting operations

## Sample Usage

Here is a simple example that demonstrates the usage of Ursina:

```python
from ursina import * 

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

app.run()
```

Additional sample games can be found here:

* [Minecraft Clone](/samples/minecraft_clone.py)
* [Platformer Game](/samples/platformer.py)

## Creating a Game with Ursina

Ursina games are developed using Python code. Follow the steps below to create a simple game:

1. Create a new Python file with the name `ursina_game.py`.
2. Insert the following code into your newly created file:

```python
from ursina import *

app = Ursina()

player = Entity(
    model = 'cube',
    color = color.orange,
    scale_y = 2
)

def update(): 
    player.x += held_keys['d'] * .1
    player.x -= held_keys['a'] * .1

app.run()
```

3. Run the game by typing the following command in your terminal:

```bash
python ursina_game.py
```

Note: If you're using Atom, we recommend installing the package atom-python-run to execute your scripts at the press of a button.

4. Now, you can move the orange box around with 'a' and 'd' keys!

To exit the game, press shift+q or click on the red x in the window's corner. To disable this functionality, insert `window.exit_button.enabled = False` into your code.

## Project Structure

```
📁docs
    📃index.txt
    📃documentation.txt
    📃inventory_tutorial.txt
    ...
    📃cheat_sheet.html
    📃tutorial_generator.py

📁samples
📁ursina
    📁audio
    📁editor
    📁fonts
    📁models
        📁procedural
    📁models_compressed
    📁prefabs

    📃__init__.py
    📃application.py
    📃audio.py
    ...
```
<footer>
This project includes several folders, such as `docs` which contains the text files for the website, as well as automatically generated documentation. The `samples` folder contains small example games, and the `ursina` folder includes the Ursina module, built-in audio clips, fonts, 3D models, and higher-level classes.
</footer>

