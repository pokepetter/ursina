import colorsys

def hsv_to_rgba(h, s, v):
    return colorsys.hsv_to_rgb(h / 360, s, v) + (1.0,)

white =         hsv_to_rgba(0, 0, 1)
smoke =         (0.961, 0.961, 0.961, 1)
light_gray =    (0.827, 0.827, 0.827, 1)
gray =          (0.5, 0.5, 0.5, 1)
black =         (0, 0, 0, 1)
red =           hsv_to_rgba(0, 1, 1)
orange =        hsv_to_rgba(30, 1, 1)
yellow =        hsv_to_rgba(60, 1, 1)
lime =          hsv_to_rgba(90, 1, 1)
green =         hsv_to_rgba(120, 1, 1)
turquoise =     hsv_to_rgba(150, 1, 1)
cyan =          hsv_to_rgba(180, 1, 1)
azure =         hsv_to_rgba(210, 1, 1)
blue =          hsv_to_rgba(240, 1, 1)
violet =        hsv_to_rgba(270, 1, 1)
magenta =       hsv_to_rgba(300, 1, 1)
pink =          hsv_to_rgba(330, 1, 1)
