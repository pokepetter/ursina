'''Translated from https://github.com/AndrewRayCode/easing-utils/blob/master/src/easing.js'''

import math

def linear(t):
    return t

def in_sine(t):
    return -1 * math.cos(t * (math.pi / 2)) + 1

def out_sine(t):
    return math.sin(t * (math.pi / 2))

def in_out_sine(t):
    return -.5 * (math.cos(math.pi * t) - 1)

def in_quad(t):
    return t * t

def out_quad(t):
    return t * (2 - t)

def in_out_quad(t):
    if t < .5:
        return 2 * t * t
    else:
        return - 1 + (4 - 2 * t) * t

def in_cubic(t):
    return t * t * t

def out_cubic(t):
    t1 = t - 1
    return t1 * t1 * t1 + 1

def in_out_cubic(t):
    if t < .5:
        return 4 * t * t * t
    else:
        return (t - 1) * (2 * t - 2) * (2 * t - 2) + 1

def in_quart(t):
    return t * t * t * t

def out_quart(t):
    t1 = t - 1
    return 1 - t1 * t1 * t1 * t1

def in_out_quart(t):
    t1 = t - 1
    if t < .5:
        return 8 * t * t * t * t
    else:
        1 - 8 * t1 * t1 * t1 * t1

def in_quint(t):
    return t * t * t * t * t

def out_quint(t):
    t1 = t - 1
    return 1 + t1 * t1 * t1 * t1 * t1

def in_out_quint(t):
    t1 = t - 1
    if t < .5:
        return 16 * t * t * t * t * t
    else:
        return 1 + 16 * t1 * t1 * t1 * t1 * t1

def in_expo(t):
    return pow(2, 10 * (t - 1))

def out_expo(t):
    return (-pow(2, -10 * t) + 1)

def in_out_expo(t):
    scaledTime = t * 2
    scaledTime1 = scaledTime - 1

    if scaledTime < 1:
        return .5 * pow(2, 10 * (scaledTime1))

    return .5 * (-pow(2, -10 * scaledTime1) + 2)

def in_circ(t):
    scaledTime = t / 1
    return -1 * (math.sqrt(1 - scaledTime * t) - 1)

def out_circ(t):
    t1 = t - 1
    return math.sqrt(1 - t1 * t1)

def in_out_circ(t):
    scaledTime = t * 2
    scaledTime1 = scaledTime - 2

    if scaledTime < 1:
        return -.5 * (math.sqrt(1 - scaledTime * scaledTime) - 1)

    return .5 * (math.sqrt(1 - scaledTime1 * scaledTime1) + 1)

def in_back(t, magnitude=1.70158):
    return t * t * ((magnitude + 1) * t - magnitude)

def out_back(t, magnitude=1.70158):
    scaledTime = (t / 1) - 1
    return (
        scaledTime * scaledTime * ((magnitude + 1) * scaledTime + magnitude)
    ) + 1

def in_out_back(t, magnitude=1.70158):
    scaledTime = t * 2
    scaledTime2 = scaledTime - 2
    s = magnitude * 1.525

    if(scaledTime < 1):
        return .5 * scaledTime * scaledTime * (
            ((s + 1) * scaledTime) - s
        )
    return .5 * (
        scaledTime2 * scaledTime2 * ((s + 1) * scaledTime2 + s) + 2
    )

def in_elastic(t, magnitude=.7):
    if(t == 0 or t == 1):
        return t
    scaledTime = t / 1
    scaledTime1 = scaledTime - 1
    p = 1 - magnitude
    s = p / (2 * math.pi) * math.asin(1)

    return -(
        pow(2, 10 * scaledTime1) *
        math.sin((scaledTime1 - s) * (2 * math.pi) / p)
    )

def out_elastic(t, magnitude=.7):
    p = 1 - magnitude
    scaledTime = t * 2

    if(t == 0 or t == 1):
        return t

    s = p / (2 * math.pi) * math.asin(1)
    return (
        pow(2, -10 * scaledTime) *
        math.sin((scaledTime - s) * (2 * math.pi) / p)
    ) + 1

def in_out_elastic(t, magnitude=0.65):
    p = 1 - magnitude
    if(t == 0 or t == 1):
        return t

    scaledTime = t * 2
    scaledTime1 = scaledTime - 1
    s = p / (2 * math.pi) * math.asin(1)

    if(scaledTime < 1):
        return -.5 * (
            pow(2, 10 * scaledTime1) *
            math.sin((scaledTime1 - s) * (2 * math.pi) / p)
        )

    return (
        pow(2, -10 * scaledTime1) *
        math.sin((scaledTime1 - s) * (2 * math.pi) / p) * .5
    ) + 1

def out_bounce(t):
    scaledTime = t / 1

    if scaledTime < (1 / 2.75):
        return 7.5625 * scaledTime * scaledTime

    elif scaledTime < (2 / 2.75):
        scaledTime2 = scaledTime - (1.5 / 2.75)
        return (7.5625 * scaledTime2 * scaledTime2) + .75

    elif scaledTime < (2.5 / 2.75):
        scaledTime2 = scaledTime - (2.25 / 2.75)
        return (7.5625 * scaledTime2 * scaledTime2) + 0.9375

    else:
        scaledTime2 = scaledTime - (2.625 / 2.75)
        return (7.5625 * scaledTime2 * scaledTime2) + 0.984375

def in_bounce(t):
    return 1 - out_bounce(1 - t)

def in_out_bounce(t):
    if(t < .5):
        return in_bounce(t * 2) * .5

    return (out_bounce((t * 2) - 1) * .5) + .5



if __name__ == '__main__':
    from ursina import curve

    '''Test all the functions:'''
    for i in dir(curve):
        item = getattr(curve, i)
        if callable(item):
            print(item.__name__, ':', item(.5))

    '''
    These are used by Entity when animating, like this:

    e = Entity()
    e.animate_y(1, curve=curve.in_expo)
    '''
