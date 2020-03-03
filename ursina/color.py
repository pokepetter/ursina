import colorsys
import random
import math
import sys
from panda3d.core import Vec4


class Color(Vec4):

    def __init__(self,*p):
        super().__init__(*p)

    def __str__(self):
        return f'Color({self[0]}, {self[1]}, {self[2]}, {self[3]})'

    @property
    def name(self):
        for key, value in colors.items():
            if value == self:
                return key

        return None

    @property
    def r(self):
        return self[0]
    @property
    def g(self):
        return self[1]
    @property
    def b(self):
        return self[2]
    @property
    def a(self):
        return self[3]

    @property
    def hsv(self):
        result = to_hsv((self[0], self[1], self[2], self[3]))
        result[0] =  math.floor(result[0] * 360)
        return result

    @property
    def h(self):
        return self.hsv[0]
    @property
    def s(self):
        return self.hsv[1]
    @property
    def v(self):
        return self.hsv[2]

    @property
    def brightness(self):
        return brightness(self)


    def invert(self):
        return inverse(self)

    def tint(self, amount):
        return tint(self, amount)



def hsv(h, s, v, a=1):
    return Color(colorsys.hsv_to_rgb((h / 360) - math.floor(h / 360), s, v) + (a,))

color = hsv

def rgba(r, g, b, a=255):
    color = Color(r, g, b, a)
    if color[0] > 1 or color[1] > 1 or color[2] > 1 or color[3] > 1:
        color = Color(tuple(c/255 for c in color))
    # color[3] = min(1, color[3])
    return color

def rgb(r, g, b, a=255):
    return rgba(r, g, b, a)

def to_hsv(color):
    return Color(colorsys.rgb_to_hsv(color[0], color[1], color[2]) + (color[3],))


def brightness(color):
    if color[0] > 1 or color[1] > 1 or color[2] > 1:
        color = Color(tuple(c/255 for c in color))
    return to_hsv(color)[2]

def inverse(color):
    color = Color(tuple(1 - c for c in color))
    color[3] = 1
    return color

def random_color():
    return Color(random.random(), random.random(), random.random(), 1)

def tint(color, amount=.2):
    return Color(
        max(min(color[0] + amount, 1), 0),
        max(min(color[1] + amount, 1), 0),
        max(min(color[2] + amount, 1), 0),
        color[3]
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
salmon =        rgb(250, 128, 114)

clear =         Color(0, 0, 0, 0)
white10 =       Color(1,1,1, 0.10)
white33 =       Color(1,1,1, 0.33)
white50 =       Color(1,1,1, 0.50)
white66 =       Color(1,1,1, 0.66)
black10 =       Color(0,0,0, 0.10)
black33 =       Color(0,0,0, 0.33)
black50 =       Color(0,0,0, 0.50)
black66 =       Color(0,0,0, 0.66)

text = smoke
light_text = smoke
dark_text = color(0, 0, .1)
text_color = light_text

# generate attributes for grayscale values. _0=black, _128=gray, 255=white
for i in range(256):
    setattr(sys.modules[__name__], '_' + str(i), color(0,0,i/255))

color_names = ('white', 'smoke', 'light_gray', 'gray', 'dark_gray', 'black',
    'red', 'orange', 'yellow', 'lime', 'green', 'turquoise', 'cyan', 'azure',
    'blue', 'violet', 'magenta', 'pink', 'brown', 'olive', 'peach', 'gold', 'salmon')
colors = dict()
for cn in color_names:
    colors[cn] = getattr(sys.modules[__name__], cn)


if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    print(color.brightness(color.blue))
    print(_3)

    p = Entity(x=-2)
    for key in color.colors:
        print(key)
        b = Button(parent=p, model=Quad(subdivisions=2), color=color.colors[key], text=key)
        b.text_entity.scale *= .5

    grid_layout(p.children, max_x=8)

    for name in ('r', 'g', 'b', 'h', 's', 'v', 'brightness'):
        print(name + ':', getattr(color.random_color(), name))

    e = Entity(model='cube', color=color.lime)
    print(e.color.name)
    app.run()
