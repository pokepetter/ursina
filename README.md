# Ursina Engine - Now with Tkinter Integration

## What is this?
This is a fork of the Ursina Engine, a game engine for Python. This fork adds Tkinter integration, allowing you to use your Ursina games in Tkinter windows.

## How do I use it?

### Installation

1. Clone this repository 
2. Copy the `ursina` folder into your project folder
3. Import `ursina` in your project using `from ursina import *`
4. Run your project like you would a normal Ursina project

### Usage

To make your Ursina game run in a Tkinter window, you just need to change a few parameters in your `Ursina()` call.

So, instead of this:
```python
app = Ursina()
```

You would do this:
```python
app = Ursina(window_type='tkinter', size=(500, 500))
```

This will make your game run in a Tkinter window with a size of 500x500 pixels.

Then if you want to use Tkinter widgets, you can just import Tkinter and use it like you normally would but instead of creating a new tk window with `tk.Tk()` you would use `app.tkRoot` or `app.getTkWindow()` which is the Tkinter window that Ursina is using.

### Example

Updated minecraft clone example from the original Ursina repo ([tkinter_minecraft_clone.py](/samples/tkinter_minecraft_clone.py)) :
```python

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import tkinter as tk
from tkinter import colorchooser


app = Ursina(window_type='tkinter',size=(500,500))

"""
Ursina part
"""

# Define a Voxel class.
# By setting the parent to scene and the model to 'cube' it becomes a 3d button.

class Voxel(Button):
    def __init__(self, position=(0,0,0)):
        super().__init__(parent=scene,
            position=position,
            model='cube',
            origin_y=.5,
            texture='white_cube',
            color=color.color(0, 0, random.uniform(.9, 1.0)),
            highlight_color=color.lime,
        )

for z in range(8):
    for x in range(8):
        voxel = Voxel(position=(x,0,z))


def input(key):
    if key == 'left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit:
            Voxel(position=hit_info.entity.position + hit_info.normal)
    if key == 'right mouse down' and mouse.hovered_entity:
        destroy(mouse.hovered_entity)
        
class pauseManager(Entity):
    def __init__(self):
        super().__init__(ignore_paused=True)


    def input(self,key):
        print(key)
        if key == 'escape':
            application.paused = not application.paused
            camera.overlay.color = color.black66 if application.paused else color.clear
            mouse.locked = not application.paused

pause_manager = pauseManager()

player = FirstPersonController()


"""
Tkinter part
"""

tkWindow = app.getTkWindow()



class DragManager:
    def __init__(self, root, ursina_window):
        self.ursina_window = ursina_window
        self.button = tk.Button(root, text="⤞")
        self.button.bind("<ButtonPress-1>", self.dnd_enter)
        self.button.bind("<ButtonRelease-1>", self.dnd_leave)
        self.root = root
        self.moving = False
        self.place_button()

    def dnd_enter(self,event):
        self.button.config(text="⤝")
        self.button.bind("<B1-Motion>", self.dnd_motion)
        self.offsetx = event.x + self.root.winfo_rootx()
        self.offsety = event.y + self.root.winfo_rooty()
        self.moving = True
        
    def dnd_leave(self, event):
        self.button.config(text="⤞")
        if not self.moving:
            return
        self.button.unbind("<B1-Motion>")
        self.moving = False
    
    def dnd_motion(self, event):
        if not self.moving:
            return
        new_pos = event.x_root-self.offsetx, event.y_root-self.offsety
        self.button.place(x=new_pos[0], y=new_pos[1])
        window.position = Vec2(new_pos)-Vec2(window.size[0]/2,0)

    def place_button(self):
        self.button.place(x=tkWindow.winfo_width()/2-self.button.winfo_reqwidth()/2+self.ursina_window.position[0], y=self.ursina_window.position[1])

drag_manager = DragManager(tkWindow, window)

color_button = tk.Button(
    tkWindow,
    text="Pick Sky Color",
    height=1,
)
def pick_color():
    color = colorchooser.askcolor(title="Choose sky color")
    window.color = Vec4(Vec3(color[0])/255,1)
    
color_button.config(command=pick_color)
color_button.place(x=0, y=0)


resize_button = tk.Button(
    tkWindow,
    text="Resize",
    height=1,
)

def resize_window():
    window.size = tkWindow.winfo_width(), tkWindow.winfo_height()
    drag_manager.place_button()

resize_button.config(command=resize_window)

resize_button.place(x=0, y=25)
app.run()
```

# Original `README.md` from [pokepetter/ursina](https://github.com/pokepetter/ursina)

# ursina    ʕ •ᴥ•ʔゝ□
An easy to use game engine/framework for python.

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
