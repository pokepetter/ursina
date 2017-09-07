import colorsys
import random
import math
from panda3d.core import Vec4

def hsv_color(h, s, v):
    return Vec4(colorsys.hsv_to_rgb((h / 360) - math.floor(h / 360), s, v) + (1,))

def to_hsv(color):
    return Vec4(colorsys.rgb_to_hsv(color[0], color[1], color[2]) + (1,))

def inverse(color):
    return Vec4(tuple(1 - c for c in color))

def random_color():
    return Vec4(random.random, random.random, random.random, 1)

white =         hsv_color(0, 0, 1)
smoke =         hsv_color(0, 0, 0.96)
light_gray =    hsv_color(0, 0, 0.75)
gray =          hsv_color(0, 0, 0.5)
dark_gray =     hsv_color(0, 0, 0.25)
black =         hsv_color(0, 0, 0)
red =           hsv_color(0, 1, 1)
orange =        hsv_color(30, 1, 1)
yellow =        hsv_color(60, 1, 1)
lime =          hsv_color(90, 1, 1)
green =         hsv_color(120, 1, 1)
turquoise =     hsv_color(150, 1, 1)
cyan =          hsv_color(180, 1, 1)
azure =         hsv_color(210, 1, 1)
blue =          hsv_color(240, 1, 1)
violet =        hsv_color(270, 1, 1)
magenta =       hsv_color(300, 1, 1)
pink =          hsv_color(330, 1, 1)

clear =         Vec4(0, 0, 0, 0)
white33 =       Vec4(1,1,1, 0.33)
white66 =       Vec4(1,1,1, 0.66)
black33 =       Vec4(0,0,0, 0.33)
black66 =       Vec4(0,0,0, 0.66)

panda_background = dark_gray
panda_button = black66
