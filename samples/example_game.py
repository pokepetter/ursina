from ursina import *    #import everything we need with just one line


class Player(Entity):   # inherits Entity, out base class for most things. Like GameObject in Unity
    def __init__(self):
        super().__init__()

        self.position = (0,1,0)
        self.position = (0,1)   # third axis is optional
        self.x = 0
        self.y = 1
        self.z = 0
        self.world_position = (0,1,0)
        self.world_x = 0

        self.rotation = (0,0,0)   # euler angles
        # target = (2,0,1)    # can also be an Entity
        # self.look_at(target)

        self.scale = (1,2,1)
        self.scale_x = 1
        self.scale_y = 2
        self.scale_z = 1
        self.world_scale = (1,2)

        self.model = 'quad' # tries to load model from /models folder
        # you can also set it to a built in procedural model
        # self.model = Circle(resolution=16)

        self.origin = (-.5, -.5)    # sets model offset. often used when working with ui

        # tries to load texture from /textures/compressed folder
        # call compress_textures() to compress .psd files and big png files
        self.texture = 'white_cube'

        self.color = color.hsv(90, 1, 1, 1) #hsv color
        self.collider = 'box'
        self.text_entity = Text(text = 'a     d', parent=scene, z=-.1)

    def input(self, key):
        print(key)

    def update(self):
        self.x += held_keys['d'] * .1
        self.x -= held_keys['a'] * .1

    def on_mouse_enter(self):
        print('enter')

    def on_mouse_exit(self):
        print('exit')

    def on_click(self):
        print('click')




if __name__ == '__main__':
    app = Ursina()
    sky = Sky()
    player = Player()

    button = Button(position=(-.5, .25), text='button_text')
    button.scale *= .2
    button.text_entity.scale /= .2
    button.tooltip = Tooltip('tooltip text')

    info_text = Text(
        '''<black>This is just an <orange>example game \n<black>so it doesn't look that <red>great''',
        y = -3,
        )

    draggable = Draggable(
        scale = (.2,.1),
        texture = 'white_cube',
        color = color.tint(color.lime, -.5),
        text = 'drag & drop!',
        # world_parent = scene
        )

    app.run()
