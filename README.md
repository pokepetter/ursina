# ursina    ʕ •ᴥ•ʔゝ□
An easy to use game engine/framework for python.  



## Getting Started
1) Install Python 3.6 or newer
2) Open cmd/terminal and type:

       pip install ursina
 
Alternatively:
1) Make sure you have git installed.
2) Open cmd/terminal and type:

       pip install panda3d
       pip install screeninfo
       pip install pillow
       pip install git+https://github.com/pokepetter/ursina.git
        
        
If you want to easily edit the source, it's recommended to clone the git repo and install as develop like this:
        
       git clone https://github.com/pokepetter/ursina.git
       python setup.py develop       
        


## Dependencies
  * python 3.6+
  * panda3d
  * screeninfo
  * pillow and psd-tools, if you want .psd compression.



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
    collision = True
    )

app.run()                       # opens a window and starts the game.
```


* [Minecraft Clone](/samples/minecraft_clone.py)

* [Platformer Game](/samples/platformer.py)


## How do I make a game?
Ursina games are made by writing Python code. You can use any text editor you want, but personally I like to use Atom.
1) Create an empty .py file called 'ursina_game.py'
2) Copy this text into your new file: 
``` python
from ursina import *                    # this will import everything we need from ursina with just one line.

class Player(Entity):                   # inherits Entity, ursina's 'god class'
    def __init__(self):
        super().__init__()
        self.model = 'cube'             # finds a 3d model by name
        self.color = color.orange
        self.scale_y = 2

    def update(self, dt):               # because Player is an Entity, update gets automatically called by the engine.
        self.x += held_keys['d'] * .1
        self.x -= held_keys['a'] * .1


app = Ursina()
player = Player()
app.run()                               # opens a window and starts the game.
```

3) Type this in the terminal to start the game:
   
       python ursina_game.py
   If you use Atom, I recommend installing the package atom-python-run to tun your scripts with the press of a button.

4) You can now move the orange box around with 'a' and 'd'!

   To close the window, you can by default, press shift+q or press the red x. to disable this, write 'window.exit_button.enabled =   False' somewhere in your code.



project oveview:

        application
            append_path()

        build -project_folder   # packaging tool. puts all dependencies into a folder so you can distribute your application

        camera(Entity)
            orthographic
            fov
            aspect_ratio

        color
            color(h, s, v, a=1)
            rgba(r, g, b, a=1)
            to_hsv(color)
            inverse(color)
            random_color()
            tint(color, amount=.2)

            white
            smoke
            light_gray
            gray
            dark_gray
            black
            red
            orange
            yellow
            lime
            green
            turquoise =     color(150, 1, 1)
            cyan
            azure
            blue
            violet
            magenta
            pink
            clear
            white33
            white50
            white66
            black33
            black50
            black66
            text = smoke
            panda_background = dark_gray
            panda_button = black66
            panda_text = smoke
            light_text = smoke
            dark_text = color(0, 0, .1)
            text_color = light_text

        Entity
            name
            enabled, visible
            parent, world_parent
            type, types

            model
            color
            texture, texture_name, texture_path, texture_size,
            texture_width, texture_height, pixels,
            texture_scale, texture_offset

            origin
            position, x, y, z
            world_position, world_x, world_y, world_z
            rotation, rotation_x, rotation_y, rotation_z
            scale, scale_x, scale_y, scale_z
            forward, back, right, left, up, down

            collision, collider
            hovered
            scripts
            children

            get_pixel(x,y)
            reparent_to()   # same as setting world_parent
            add_script(module_name/class/instance)
            remove_script(module_name)
            look_at()
            has_ancestor()

            animate(name, value, duration=.1, delay=0, curve='ease_in_expo', resolution=None, interrupt=True)
            animate_position(), animate_x(), animate_y(), animate_z()
            animate_rotation(), animate_rotation_x(), animate_rotation_y(), animate_rotation_z()
            animate_scale(), animate_scale_x(), animate_scale_y(), animate_scale_z()
            shake(duration=.2, magnitude=1, speed=.05)
            animate_color()

            # these functions gets automatically called if they exsist:
            start(self)
            input(self, key)
            update(self, dt)
            on_mouse_enter(self)
            on_mouse_exit(self)
            on_click(self)
            on_destroy(self)

        input
            held_keys   # dict that hold key states.

        internal_prefabs
            Animation(Entity)   # for 2D animations
            Button
            Cursor
            Draggable   # for easy drag and drop
            Grid(w, h, thickness)
            Mesh(verts, tris=None, colors=None, uvs=None, normals=None, static=True, mode='triangle', thickness=1)
                modes
                    'triangle'
                    'tristrip'
                    'ngon'
                    'line'
                    'lines'
                    'point'
                thickness
            Plane
            Sky
            Sprite  # scales to fit texture dimensions
            Text
                text
                font
                line_height
                width
                height
                wordwrap
                align
                    'left', 'center', 'right'

                # supports inline scale and color tags:
                # example_text = Text('<scale:1.5><orange>Title \n<scale:1>Increase <red>max health <default>with 25%.')
            Tooltip

        mouse
            enabled
            locked      # lock to center of screen for first person controller and such
            position
            x, y
            delta
            delta_drag
            velocity
            double_click_distance = .5      # in seconds
            left, right, middle

            normal
            point
            collision
                collided
                entity
                position
                normal

        ursinamath
            distance(entity_a, entity_b)
            lerp(a, b, t)
            inverselerp(a, b, t)
            clamp(value, floor, ceiling)
            chunk_list(l, chunk_size)   # yield successive chunks from list



        ursinastuff
            invoke(function, *args, **kwargs)
            destroy(entity, delay=0)
            compress_textures(name=None)

        raycaster
            raycast(self, origin, direction, dist=1000, traverse_target=None, debug=False) # returns Hit
            Hit
                hit
                entity
                distance
                point

        scene
            camera
            ui

        useful
            camel_to_snake(value)
            snake_to_camel(value)
            multireplace(string, replacements, ignore_case=False)
            printvar(var)

        window
            center_on_screen
            size
            position
            fullscreen
            color       # clear color / background
            fps_counter
            exit_button
