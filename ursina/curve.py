'''Translated from https://github.com/AndrewRayCode/easing-utils/blob/master/src/easing.js'''

from math import cos, pi, sqrt, sin, asin, floor


def linear(t):
    return t


def in_sine(t):
    return -1 * cos(t * (pi / 2)) + 1


def out_sine(t):
    return sin(t * (pi / 2))


def in_out_sine(t):
    return -.5 * (cos(pi * t) - 1)


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
    return -pow(2, -10 * t) + 1


def in_out_expo(t):
    scaledTime = t * 2
    scaledTime1 = scaledTime - 1

    if scaledTime < 1:
        return .5 * pow(2, 10 * scaledTime1)

    return .5 * (-pow(2, -10 * scaledTime1) + 2)


def in_circ(t):
    scaledTime = t / 1
    return -1 * (sqrt(1 - scaledTime * t) - 1)


def out_circ(t):
    t1 = t - 1
    return sqrt(1 - t1 * t1)


def in_out_circ(t):
    scaledTime = t * 2
    scaledTime1 = scaledTime - 2

    if scaledTime < 1:
        return -.5 * (sqrt(1 - scaledTime * scaledTime) - 1)

    return .5 * (sqrt(1 - scaledTime1 * scaledTime1) + 1)


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

    if scaledTime < 1:
        return .5 * scaledTime * scaledTime * (
                ((s + 1) * scaledTime) - s
        )
    return .5 * (
            scaledTime2 * scaledTime2 * ((s + 1) * scaledTime2 + s) + 2
    )


def in_elastic(t, magnitude=.7):
    if t == 0 or t == 1:
        return t
    scaledTime = t / 1
    scaledTime1 = scaledTime - 1
    p = 1 - magnitude
    s = p / (2 * pi) * asin(1)

    return -(
            pow(2, 10 * scaledTime1) *
            sin((scaledTime1 - s) * (2 * pi) / p)
    )


def out_elastic(t, magnitude=.7):
    p = 1 - magnitude
    scaledTime = t * 2

    if t == 0 or t == 1:
        return t

    s = p / (2 * pi) * asin(1)
    return (
                   pow(2, -10 * scaledTime) *
                   sin((scaledTime - s) * (2 * pi) / p)
           ) + 1


def in_out_elastic(t, magnitude=0.65):
    p = 1 - magnitude
    if t == 0 or t == 1:
        return t

    scaledTime = t * 2
    scaledTime1 = scaledTime - 1
    s = p / (2 * pi) * asin(1)

    if scaledTime < 1:
        return -.5 * (
                pow(2, 10 * scaledTime1) *
                sin((scaledTime1 - s) * (2 * pi) / p)
        )

    return (
                   pow(2, -10 * scaledTime1) *
                   sin((scaledTime1 - s) * (2 * pi) / p) * .5
           ) + 1


def out_bounce(t):
    scaledTime = t / 1

    if scaledTime < 1 / 2.75:
        return 7.5625 * scaledTime * scaledTime

    elif scaledTime < 2 / 2.75:
        scaledTime2 = scaledTime - (1.5 / 2.75)
        return (7.5625 * scaledTime2 * scaledTime2) + .75

    elif scaledTime < 2.5 / 2.75:
        scaledTime2 = scaledTime - (2.25 / 2.75)
        return (7.5625 * scaledTime2 * scaledTime2) + 0.9375

    else:
        scaledTime2 = scaledTime - (2.625 / 2.75)
        return (7.5625 * scaledTime2 * scaledTime2) + 0.984375


def in_bounce(t):
    return 1 - out_bounce(1 - t)


def in_out_bounce(t):
    if t < .5:
        return in_bounce(t * 2) * .5

    return (out_bounce((t * 2) - 1) * .5) + .5


# generate boomeranged versions of all the functions
import sys
from textwrap import dedent

for e in dir(sys.modules[__name__]):
    item = getattr(sys.modules[__name__], e)
    if callable(item):
        exec(dedent(f'''
            def {e}_boomerang(t):
                if t < .5:
                    return {e}(t*2)
                else:
                    return {e}(1-((t-.5)*2))
        '''))


# bezier code is translated  from WebKit implementation
class CubicBezier:
    __slots__ = ['a', 'b', 'c', 'd', 'cx', 'bx', 'ax', 'cy', 'by', 'ay']

    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        # pre-calculate the polynomial coefficients
        # irst and last control points are implied to be (0,0) and (1.0, 1.0)
        self.cx = 3.0 * a
        self.bx = 3.0 * (c - a) - self.cx
        self.ax = 1.0 - self.cx - self.bx

        self.cy = 3.0 * b
        self.by = 3.0 * (d - b) - self.cy
        self.ay = 1.0 - self.cy - self.by

    def sample_curve_x(self, t):
        return ((self.ax * t + self.bx) * t + self.cx) * t

    def sample_curve_y(self, t):
        return ((self.ay * t + self.by) * t + self.cy) * t

    def sample_curve_derivative_x(self, t):
        return (3.0 * self.ax * t + 2.0 * self.bx) * t + self.cx

    def calculate(self, x, epsilon=.0001):
        return self.sample_curve_y(self.solve_curve_x(x, epsilon))

    def solve_curve_x(self, t, epsilon=.0001):
        # First try a few iterations of Newton's method -- normally very fast.
        t0 = 0
        t1 = 0
        t2 = 0
        x2 = 0
        d2 = 0
        i = 0

        # t2 = t
        # for i in range(8):
        #     x2 = self.sample_curve_x(t2) - t
        #     if abs(x2) < epsilon:
        #         return t2
        #     d2 = self.sample_curve_derivative_x(t2)
        #     if abs(d2) < epsilon:
        #         break
        #
        #     t2 = t2 - x2 / d2

        # No solution found - use bi-section
        t0 = 0.0
        t1 = 1.0
        t2 = t

        if t2 < t0:
            return t0
        if t2 > t1:
            return t1

        while t0 < t1:
            x2 = self.sample_curve_x(t2)
            if abs(x2 - t) < epsilon:
                return t2
            if t > x2:
                t0 = t2
            else:
                t1 = t2

            t2 = (t1 - t0) * .5 + t0

        # Give up
        return t2


if __name__ == '__main__':
    '''Draws a sheet with every curve and its name'''
    from ursina import *

    app = Ursina()
    camera.orthographic = True
    camera.fov = 16
    camera.position = (9, 6)
    window.color = color.black

    i = 0
    for e in dir(curve):
        try:
            item = getattr(curve, e)
            print(item.__name__, ':', item(.75))
            curve_renderer = Entity(
                model=Mesh(vertices=[Vec3(i / 31, item(i / 31), 0) for i in range(32)], mode='line', thickness=2),
                color=color.light_gray)
            row = floor(i / 8)
            curve_renderer.x = (i % 8) * 2.5
            curve_renderer.y = row * 1.75
            label = Text(parent=curve_renderer, text=item.__name__, scale=8, color=color.gray, y=-.1)
            i += 1
        except:
            pass

    c = CubicBezier(0, .5, 1, .5)
    print('-----------', c.calculate(.23))
    # for x, c in enumerate([curve.CubicBezier(0,1,1,0), curve.CubicBezier(0,.5,1,.5), curve.CubicBezier(0,0,0,0), curve.CubicBezier(0,.7,1,.3)]):
    #     verts = [Vec3(i/20, c.calculate(i/20), 0) for i in range(20)]
    #     Entity(parent=camera.ui, model=Mesh(vertices=verts, mode='line', thickness=3), scale=.25, x=-.5+(x*.25))

    window.exit_button.visible = False
    window.fps_counter.enabled = False
    app.run()
    '''
    These are used by Entity when animating, like this:

    e = Entity()
    e.animate_y(1, curve=curve.in_expo)

    e2 = Entity(x=1.5)
    e2.animate_y(1, curve=curve.CubicBezier(0,.7,1,.3))
    '''
