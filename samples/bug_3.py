from ursina import *

app = Ursina()

start = Entity(model='sphere', scale=.2, color=color.red, position=(-.5,-.25))
end = Entity(model='sphere', scale=.2, color=color.red, position=(.5,.25))

line = Entity(model='cube', origin_z=-.5, position=start, scale=.05, color=color.azure)


# line.look_at(end)
# line.scale_z = distance(start, end)


app.run()
