from ursina import *
from ursina.shaders import *

app = Ursina()

counter = 0
target_x = -0.4

pill_pivot = Entity(scale=.075, parent=camera.ui,
                    x=0,
                    y=0,
                    z=0)


pill = Entity(model='quad', texture='pill.png', parent=pill_pivot, scale=(1.5, .7))
circle = Entity(124, model='circle', collider='box', color=color.white, parent=pill_pivot, scale=.333, x=-0.4,
                always_on_top=True)


def update():
    global counter, target_x
    if mouse.hovered_entity == circle and mouse.left:
        target_x = 0.4 if counter == 0 else -0.4
        counter = 1 if counter == 0 else 0
        print(circle.x)
    circle.x = lerp(circle.x, target_x, time.dt * 5)

    if circle.x < -.1:
        circle.color = color.red
    elif circle.x > .1:
        circle.color = color.green


app.run()
