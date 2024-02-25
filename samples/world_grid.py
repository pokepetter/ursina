from ursina import *


app = Ursina()

r = 8
for i in range(1, r):
    t = i/r
    s = 4*i
    print(s)
    grid = Entity(model=Grid(s,s), scale=s, color=color.hsv(0,0,.8,lerp(.8,0,t)), rotation_x=90, y=i/1000)
    subgrid = duplicate(grid)
    subgrid.model = Grid(s*4, s*4)
    subgrid.color = color.hsv(0,0,.4,lerp(.8,0,t))
    EditorCamera()

app.run()
