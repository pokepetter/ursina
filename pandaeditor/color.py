import colorsys
import random
import math
from panda3d.core import Vec4

def color(h, s, v, a=1):
    return Vec4(colorsys.hsv_to_rgb((h / 360) - math.floor(h / 360), s, v) + (a,))

def rgba(r, g, b, a=1):
    return Vec4(r, g, b, a)

def to_hsv(color):
    return Vec4(colorsys.rgb_to_hsv(color[0], color[1], color[2]) + (color[3],))

def inverse(color):
    return Vec4(tuple(1 - c for c in color))

def random_color():
    return Vec4(random.random(), random.random(), random.random(), 1)


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

clear =         Vec4(0, 0, 0, 0)
white33 =       Vec4(1,1,1, 0.33)
white66 =       Vec4(1,1,1, 0.66)
black33 =       Vec4(0,0,0, 0.33)
black66 =       Vec4(0,0,0, 0.66)

text = smoke

panda_background = dark_gray
panda_button = black66
panda_text = smoke
text_color = panda_text
