from ursina import *


app = Ursina()

start_point = Draggable(model='circle', color=color.orange, scale=.025, position=(-0,-0))
end_point = Draggable(model='circle', color=color.orange, scale=.025, position=(.2,.1))

line = Entity(parent=camera.ui, model='line', origin_x=-.5) # set origin_x = -.5 o it starts at the left and not the middle.

def update():
    line.position = start_point.position
    line.look_at_2d(end_point)  # could also ise .look_at() (3d) for this.
    line.rotation_z -= 90 # look_at_2d assumes up as forward, so offset by -90 degrees.
    line.scale_x = distance_2d(start_point, end_point)

app.run()
