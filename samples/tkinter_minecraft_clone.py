'''
Disclaimer: This solution is not scalable for creating a big world.
Creating a game like Minecraft requires specialized knowledge and is not as easy
to make as it looks.

You'll have to do some sort of chunking of the world and generate a combined mesh
instead of separate blocks if you want it to run fast. You can use the Mesh class for this.

You can then use blocks with colliders like in this example in a small area
around the player so you can interact with the world.
'''

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