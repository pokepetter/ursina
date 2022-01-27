import operator
from math import sqrt, sin, acos
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


def distance_2d(a, b):
    if hasattr(a, 'position'): a = a.position
    if hasattr(b, 'position'): b = b.position

    return sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)


def distance_xz(a, b):
    if hasattr(a, 'position'): a = a.position
    if hasattr(b, 'position'): b = b.position

    return sqrt((b[0] - a[0])**2 + (b[2] - a[2])**2)


def magnitude(a):
    return sqrt(sum(a[i]**2 for i in range(len(a))))

def dot(a, b):
    return sum(a[i]*b[i] for i in range(len(a)))

def cross(a, b):
    if len(a) == 2:
        return a[0]*b[1] - a[1]*b[0]
    
    if len(a) == 3:
        if isinstance(a, (list, tuple)):
            return [a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0]]
        else:
            return Vec3(a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0])
    return a

def reflect(a, normal):
    return a - normal * dot(a, normal) * 2

def normalize(a):
    mag = magnitude(a)
    if isinstance(a, tuple):
        a = list(a)
    else:
        a = type(a)(a)
    for i in range(len(a)):
        a[i] /= mag
    return a

def sign(a):
    if isinstance(a, (int, float)):
        return 1 if a > 0 else -1
    if isinstance(a, (list, tuple)):
        return [1 if a[i] > 0 else -1 for i in range(len(a))]
    if isinstance(a, (Vec2, Vec3, Vec4, LVector3f)):
        a = type(a)(a)
        for i in range(len(a)):
            a[i] = 1 if a[i] > 0 else -1
    return a


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


def slerp(q1, q2, t):
    costheta = q1.dot(q2)
    if costheta < 0.0:
        costheta = -costheta
        q1 = q1.conjugate()
    elif costheta > 1.0:
        costheta = 1.0

    theta = acos(costheta)
    if abs(theta) < 0.01:
        return q2

    sintheta = sqrt(1.0 - costheta * costheta)
    if abs(sintheta) < 0.01:
        return (q1+q2)*0.5

    r1 = sin((1.0 - t) * theta) / sintheta
    r2 = sin(t * theta) / sintheta
    return (q1*r1) + (q2*r2)


def move_towards(a, b, amount):
    if isinstance(a, (Vec2, Vec3, Vec4, LVector3f)):
        delta = b - a
        delta_length = magnitude(delta)
        if delta_length < amount:
            return b
        return a + delta / delta_length * amount 
    
    if isinstance(a, (list, tuple)):
        size = range(len(a))
        delta = [(b[i] - a[i]) for i in size]
        delta_length = magnitude(delta)
        if delta_length < amount:
           return a
        m = min(delta_length, amount) / delta_length
        return [a[i] + delta[i] * m for i in size]
    
    if isinstance(a, (int, float)):
        if abs(b - a) < amount:
            return b
        return a + (amount if a < b else -amount)
    
    return a


def move_towards_angle(a, b, amount):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return a
    a, b = a % 360, b % 360

    if abs(b - a) > 180:
        b += 360 if a > b else -360
    if abs(b - a) < amount:
        return b
    return a + (amount if b > a else -amount)

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

    print(move_towards(Vec2(0,0), Vec2(1,-1), 1))
    print(move_towards((0,0,2), (2,1,0), 1))
    print(move_towards_angle(340, 20, 10))

    print(magnitude(Vec3(1,2,3)))
    print(normalize(Vec3(1,2,3)))
    print(dot(Vec3(1,1,0), Vec3(0,1,1)))
    print(cross((3,1,3), (2,2,1)))
    
    print(sign(-99))
    print(sign(Vec3(1,-2,-3)))

    e3 = Entity(model = 'cube', position = (-3,1,0))
    target = Vec3(-3,1,1)

    window.borderless = False
    def update():
        global velocity
        e3.position = move_towards(e3.position, target, 5 * time.dt)
        
    def input(key):
        if key ==  'space':
            global target
            target = -target

    app.run()
