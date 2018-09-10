import colorsys
import random
import math
from panda3d.core import Vec4

def color(h, s, v, a=1):
    return Vec4(colorsys.hsv_to_rgb((h / 360) - math.floor(h / 360), s, v) + (a,))

def rgba(r, g, b, a=255):
    color = Vec4(r, g, b, a)
    if color[0] > 1 or color[1] > 1 or color[2] > 1:
        color = Vec4(tuple(c/255 for c in color))
    color[3] = min(1, color[3])
    return color

def rgb(r, g, b, a=255):
    return rgba(r, g, b, a)

def to_hsv(color):
    return Vec4(colorsys.rgb_to_hsv(color[0], color[1], color[2]) + (color[3],))

def inverse(color):
    color = Vec4(tuple(1 - c for c in color))
    color[3] = 1
    return color

def random_color():
    return Vec4(random.random(), random.random(), random.random(), 1)

def tint(color, amount=.2):
    return Vec4(
        max(min(color[0] + amount, 1), 0),
        max(min(color[1] + amount, 1), 0),
        max(min(color[2] + amount, 1), 0),
        1
        )


white =         color(0, 0, 1)
smoke =         color(0, 0, 0.96)
light_gray =    color(0, 0, 0.75)
gray =          color(0, 0, 0.5)
dark_gray =     color(0, 0, 0.25)
black =         color(0, 0, 0)
red =           color(0, 1, 1)
orange =        color(30, 1, 1)
yellow =        color(60, 1, 1)
lime =          color(90, 1, 1)
green =         color(120, 1, 1)
turquoise =     color(150, 1, 1)
cyan =          color(180, 1, 1)
azure =         color(210, 1, 1)
blue =          color(240, 1, 1)
violet =        color(270, 1, 1)
magenta =       color(300, 1, 1)
pink =          color(330, 1, 1)

brown =         rgb(165, 42, 42)
olive =         rgb(128, 128, 0)
peach =         rgb(255, 218, 185)
gold =          rgb(255, 215, 0)
salmon =        rgb(250,128,114)

clear =         Vec4(0, 0, 0, 0)
white33 =       Vec4(1,1,1, 0.33)
white50 =       Vec4(1,1,1, 0.50)
white66 =       Vec4(1,1,1, 0.66)
black33 =       Vec4(0,0,0, 0.33)
black50 =       Vec4(0,0,0, 0.50)
black66 =       Vec4(0,0,0, 0.66)

text = smoke
light_text = smoke
dark_text = color(0, 0, .1)
text_color = light_text


if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    p = Entity()
    colors = [(var, getattr(color, var)) for var in dir(color)] # (name, value)
    colors = [col for col in colors if type(col[1]) is Vec4]

    for col in colors:
        print(col)
        b = Button(parent=p, color=col[1], text=col[0])
        b.text_entity.color = color.inverse(col[1])
        b.text_entity.scale *= .75

    grid_layout(p.children, max_x=8, origin=(0,0))

    app.run()
