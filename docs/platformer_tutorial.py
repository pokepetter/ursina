# Start by importing ursina and creating a window.
from ursina import *
app = Ursina()

# ## Using the built in platformer controller
#
# A simple way to get stared is to use the built in platformer controller.
# It's pretty basic, so you might want to write your own at a later point.
# It is however a good starting point, so let's import it like this:
from ursina.prefabs.platformer_controller_2d import PlatformerController2d
player = PlatformerController2d(y=1, z=.01, scale_y=1, max_jumps=2)

# You can change settings like jump_height, walk_speed, and gravity.
# If you want to larn more about how it works you can read its code here:
# https://github.com/pokepetter/ursina/blob/master/ursina/prefabs/platformer_controller_2d.py
#
# If we try to play the game right now, you'll fall for all infinity, so let's add a ground:
ground = Entity(model='quad', scale_x=10, collider='box', color=color.black)

# ## Making a "level editor"
#
# Now, it works, but it's a pretty boring game, so let's make a more interesting level.
# There are many ways to go about making a level, but for this we'll make an image
# where we can simply draw the level and then generate a level based on that.
#
# # image platformer_tutorial_level.png
# ↑
# Make sure to save this image to same folder or below as your script.
#
# To generate the level we'll loop through all the pixels in the image above and do
# something based on the color of the pixel. If it's white, it's air, so we'll skip it.
# Now, we *could* create an Entity for each tile, but that's slower to render than one Entity with a custom model.
# To make the model, we'll use the Mesh class. You'll have to be somewhat familiar with
# what meshes are to do this, and know what vertices and uvs are. However, we'll just be
# copying the quad model and offset the vertices. If we wanted to use a tileset with different
# graphics for each tile, we'd scale and offset the uvs as well.

quad = load_model('quad', use_deepcopy=True)


level_parent = Entity(model=Mesh(vertices=[], uvs=[]), texture='white_cube')
def make_level(texture):
    # destroy every child of the level parent.
    # This doesn't do anything the first time the level is generated, but if we want to update it several times
    # this will ensure it doesn't just create a bunch of overlapping entities.
    [destroy(c) for c in level_parent.children]

    for y in range(texture.height):
        collider = None
        for x in range(texture.width):
            col = texture.get_pixel(x,y)

            # If it's black, it's solid, so we'll place a tile there.
            if col == color.black:
                level_parent.model.vertices += [Vec3(*e) + Vec3(x+.5,y+.5,0) for e in quad.generated_vertices] # copy the quad model, but offset it with Vec3(x+.5,y+.5,0)
                level_parent.model.uvs += quad.uvs
                # Entity(parent=level_parent, position=(x,y), model='cube', origin=(-.5,-.5), color=color.gray, texture='white_cube', visible=True)
                if not collider:
                    collider = Entity(parent=level_parent, position=(x,y), model='quad', origin=(-.5,-.5), collider='box', visible=False)
                else:
                    # instead of creating a new collider per tile, stretch the previous collider right.
                    collider.scale_x += 1
            else:
                collider = None

            # If it's green, we'll place the player there. Store this in player.start_position so we can reset the plater position later.
            if col == color.green:
                player.start_position = (x, y)
                player.position = player.start_position

    level_parent.model.generate()

make_level(load_texture('platformer_tutorial_level'))   # generate the level

# ## Positioning the camera
#
# Set the camera to orthographic so there's no perspective.
# Move the camera to the middle of the level and set the fov so the level fits nicely.
# Setting the fov on an orthographic camera means setting how many units vertically the camera can see.
camera.orthographic = True
camera.position = (30/2,8)
camera.fov = 16


# ## Adding player graphics and animations
#
# Loads an image sequence as a frame animation.
# So if you have some frames named image_000.png, image_001.png, image_002.png and so on,
# you can load it like this: Animation('image')
# You can also load a .gif by including the file type: Animation('image.gif')
# player.walk_animation = Animation('player_walk')

# the platformer controller has an Animator and will toggle the state based on
# whether it's standing still, is walking or is jumping.
# All the Animator does is to make sure only one Animation is enabled at the same time.
# Otherwise they would overlap.
# self.animator = Animator({'idle' : None, 'walk' : None, 'jump' : None})
player.traverse_target = level_parent
enemy = Entity(model='cube', collider='box', color=color.red, position=(16,5,-.1))
def update():
    if player.intersects(enemy).hit:
        print('die')
        player.position = player.start_position


# ## Start the game
#
app.run()

# ## Adding level graphics
#
# Coming later
pass
