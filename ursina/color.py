import colorsys
import random
import sys
from math import floor

from ursina.scripts.property_generator import generate_properties_for_class
from ursina.vec4 import Vec4


@generate_properties_for_class()
class Color(Vec4):
    def __init__(self,*p):
        super().__init__(*p)

    def __repr__(self):
        return f'Color({self[0]}, {self[1]}, {self[2]}, {self[3]})'

    def name_getter(self):
        for key, value in colors.items():
            if value == self:
                return key
        return None

    def rgb_getter(self):
        return (self[0], self[1], self[2])
    def rgba_getter(self):
        return (self[0], self[1], self[2], self[3])
    def rgb32_getter(self):
        return tuple(int(e*255) for e in self.rgb)
    def rgba32_getter(self):
        return tuple(int(e*255) for e in self.rgba)

    def r_getter(self):
        return self[0]
    def g_getter(self):
        return self[1]
    def b_getter(self):
        return self[2]
    def a_getter(self):
        return self[3]

    def hsv_getter(self):
        result = to_hsv((self[0], self[1], self[2], self[3]))
        result[0] =  floor(result[0] * 360)
        return result

    def h_getter(self):
        return self.hsv[0]
    def s_getter(self):
        return self.hsv[1]
    def v_getter(self):
        return self.hsv[2]

    def brightness_getter(self):
        return brightness(self)

    def invert(self):
        return inverse(self)

    def tint(self, amount):
        return tint(self, amount)


def hsv(h, s, v, a=1.0):
    return Color(colorsys.hsv_to_rgb((h / 360) - floor(h / 360), s, v) + (a,))

def rgba32(r, g, b, a=255):
    return Color(r/255, g/255, b/255, a/255)

rgb32 = rgba32   # alias for rgba32()

def rgba(r, g, b, a=1.0):
    return Color(r, g, b, a)

rgb = rgba  # alias for rgba()

def to_hsv(color):
    return Color(colorsys.rgb_to_hsv(color[0], color[1], color[2]) + (color[3],))

def hex(value):
    if isinstance(value, int):
        return rgb(*tuple((value >> (8 * i)) & 0xff for i in [2,1,0]))

    if value.startswith('#'):
        value = value[1:]
    return rgb32(*tuple(int(value[i:i+2], 16) for i in (0, 2, 4)))

def rgb_to_hex(r, g, b, a=1.0):
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}{int(a*255):02x}"


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


white =         hsv(0, 0, 1)
smoke =         hsv(0, 0, 0.96)
light_gray =    hsv(0, 0, 0.75)
gray =          hsv(0, 0, 0.5)
dark_gray =     hsv(0, 0, 0.25)
black =         hsv(0, 0, 0)
red =           hsv(0, 1, 1)
orange =        hsv(30, 1, 1)
yellow =        hsv(60, 1, 1)
lime =          hsv(90, 1, 1)
green =         hsv(120, 1, 1)
turquoise =     hsv(150, 1, 1)
cyan =          hsv(180, 1, 1)
azure =         hsv(210, 1, 1)
blue =          hsv(240, 1, 1)
violet =        hsv(270, 1, 1)
magenta =       hsv(300, 1, 1)
pink =          hsv(330, 1, 1)

brown =         rgb32(165, 42, 42)
olive =         rgb32(128, 128, 0)
peach =         rgb32(255, 218, 185)
gold =          rgb32(255, 215, 0)
salmon =        rgb32(250, 128, 114)

clear =         rgba(0, 0, 0, 0)
white10 =       rgba(1,1,1, 0.10)
white33 =       rgba(1,1,1, 0.33)
white50 =       rgba(1,1,1, 0.50)
white66 =       rgba(1,1,1, 0.66)
black10 =       rgba(0,0,0, 0.10)
black33 =       rgba(0,0,0, 0.33)
black50 =       rgba(0,0,0, 0.50)
black66 =       rgba(0,0,0, 0.66)
black90 =       rgba(0,0,0, 0.90)

text = smoke
light_text = smoke
dark_text = hsv(0, 0, .1)
text_color = light_text

# generate attributes for grayscale values. _0=black, _128=gray, 255=white
for i in range(256):
    setattr(sys.modules[__name__], '_' + str(i), hsv(0,0,i/255))

color_names = ('white', 'smoke', 'light_gray', 'gray', 'dark_gray', 'black',
    'red', 'orange', 'yellow', 'lime', 'green', 'turquoise', 'cyan', 'azure',
    'blue', 'violet', 'magenta', 'pink', 'brown', 'olive', 'peach', 'gold', 'salmon')
colors = dict()
for cn in color_names:
    colors[cn] = getattr(sys.modules[__name__], cn)


if __name__ == '__main__':
    from ursina import *
    from ursina import Button, Entity, Quad, Ursina, color, grid_layout
    from ursina.ursinastuff import _test
    app = Ursina()

    _test(hsv(30,1,1) == color.orange)
    _test(color.brightness(color.blue) == 1.0)
    _test(color.red.rgb == (1.0, 0.0, 0.0))
    _test(color.red.rgba == (1.0, 0.0, 0.0, 1.0))

    p = Entity(x=-2)
    for key in color.colors:
        print(key)
        b = Button(parent=p, model=Quad(0), color=color.colors[key], text=key)
        b.text_entity.scale *= .5

    grid_layout(p.children, max_x=8)

    for name in ('r', 'g', 'b', 'h', 's', 'v', 'brightness'):
        print(name + ':', getattr(color.random_color(), name))

    e = Entity(model='cube', color=color.lime)
    print(e.color.name)
    print('rgb to hex:', color.rgb_to_hex(*color.blue))
    # e.color = hex('ced9a9')
    e.color = color.rgba32(1,2,3)
    app.run()
