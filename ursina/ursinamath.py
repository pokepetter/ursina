import operator
from math import sqrt
from panda3d.core import Vec4, LVector3f, Mat3, Mat4
from ursina.vec2 import Vec2
from ursina.vec3 import Vec3
from ursina.color import Color
internal_sum = sum


def distance(a, b):
    try:
        # dist = [abs(e) for e in (a - b)]
        dist = abs(a[0] - b[0])
        dist += abs(a[1] - b[1])
        dist += abs(a[2] - b[2])
        dist += abs(a[3] - b[3])
        # print('color distance', a, b)
        return dist
    except:
        pass

    # if input is Entity, convert to positions
    if hasattr(a, 'position'): a = a.position
    if hasattr(b, 'position'): b = b.position

    dist = sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2 + (b[2] - a[2])**2)
    # print('------------DIST:', dist)
    return dist


def distance2d(a, b):
    if hasattr(a, 'position'): a = a.position
    if hasattr(b, 'position'): b = b.position

    return sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)


def distance_xz(a, b):
    if hasattr(a, 'position'): a = a.position
    if hasattr(b, 'position'): b = b.position

    return sqrt((b[0] - a[0])**2 + (b[2] - a[2])**2)


def lerp(a, b, t):
    if isinstance(a, (int, float, complex)):
        return a + (b - a) * t

    elif isinstance(a, Color) and isinstance(b, Color):
        col = [lerp(e[0], e[1], t) for e in zip(a,b)]
        return Color(col[0], col[1], col[2], col[3])

    elif isinstance(a, (tuple, list, Vec2, Vec3, Vec4, LVector3f)) and isinstance(b, (tuple, list, Vec2, Vec3, Vec4, LVector3f)):
        lerped = list()
        for i in range(min(len(a), len(b))):
            lerped.append(lerp(a[i], b[i], t))

        if isinstance(a, (tuple, list)):
            return type(a)(lerped)
        else:
            return type(a)(*lerped)
    else:
        print(f'''can't lerp types {type(a)} and {type(b)}''')


def inverselerp(a, b, t) :
    return (a - b) / (t - b)


def clamp(value, floor, ceiling):
    return max(min(value, ceiling), floor)


def round_to_closest(value, step=0):
    if not step:
        return value

    step = 1/step
    return round(value * step) / step


def chunk_list(l, chunk_size):
    # yield successive chunks from list
    for i in range(0, len(l), chunk_size):
        yield l[i:i + chunk_size]


def size_list():
    #return a list of current python objects sorted by size
    globals_list = list()
    globals_list.clear()
    for e in globals():
        # object, size
        globals_list.append([e, sys.getsizeof(e)])
    globals_list.sort(key=operator.itemgetter(1), reverse=True)
    print('scene size:', globals_list)


def sum(l):
    try:
        return internal_sum(l)
    except:
        pass

    total = l[0].__class__()
    for e in l:
        total += e

    return total


if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    e1 = Entity(position = (0,0,0))
    e2 = Entity(position = (0,1,1))
    distance(e1, e2)
    distance_xz(e1, e2.position)

    between_color = lerp(color.lime, color.magenta, .5)
    print(between_color)
    print(lerp((0,0), (0,1), .5))
    print(lerp(Vec2(0,0), Vec2(0,1), .5))
    print(lerp([0,0], [0,1], .5))

    print(round(Vec3(.38, .1351, 353.26), 2))

    app.run()
