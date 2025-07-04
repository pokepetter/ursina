from math import sqrt, sin, acos, pi, cos, floor
from math import hypot
from panda3d.core import Vec4, LVector3f
from ursina.vec2 import Vec2
from ursina.vec3 import Vec3
from ursina import color
from ursina.color import Color
_sum = sum


def distance(a, b):
    if isinstance(a, (Color, Vec4)):
        dist = abs(a[0] - b[0])
        dist += abs(a[1] - b[1])
        dist += abs(a[2] - b[2])
        dist += abs(a[3] - b[3])
        return dist

    # if input is Entity, convert to positions
    if hasattr(a, 'world_position'): a = a.world_position
    if hasattr(b, 'world_position'): b = b.world_position

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


def lerp(a, b, t):
    if isinstance(a, (int, float, complex)):
        return a + (b - a) * t

    elif isinstance(a, Color) and isinstance(b, Color):
        col = [lerp(e[0], e[1], t) for e in zip(a,b)]
        return Color(col[0], col[1], col[2], col[3])

    elif isinstance(a, (tuple, list, Vec2, Vec3, Vec4, LVector3f)) and isinstance(b, (tuple, list, Vec2, Vec3, Vec4, LVector3f)):
        lerped = []
        for i in range(min(len(a), len(b))):
            lerped.append(lerp(a[i], b[i], t))

        if isinstance(a, (tuple, list)):
            return type(a)(lerped)
        else:
            return type(a)(*lerped)
    else:
        raise TypeError(f'''can't lerp types {type(a)} and {type(b)}''')

def inverselerp(a, b, value):   # get *where* between a and b, value is (0.0 - 1.0)
    if a == b:
        return .5
    return (value - a) / (b - a)

if __name__ == '__main__':
    from ursina.ursinastuff import _test
    _test(inverselerp(0, 100, 50) == .5)
    _test(lerp(0, 100, .5) == 50)


def lerp_exponential_decay(a, b, decay_rate):    # frame-rate independent lerp for use in update. use this instead of lerp(a, b, time.dt) in update.
    return lerp(a, b, 1 - pow(0.01, decay_rate))


def lerp_angle(start_angle, end_angle, t):
    start_angle = start_angle % 360
    end_angle = end_angle % 360
    angle_diff = (end_angle - start_angle + 180) % 360 - 180
    result_angle = start_angle + t * angle_diff
    result_angle = (result_angle + 360) % 360
    return result_angle


def slerp(q1, q2, t):
    costheta = q1.dot(q2)

    # ensure shortest path by flipping q2 if dot product is negative
    if costheta < 0.0:
        q2 = -q2
        costheta = -costheta

    costheta = clamp(costheta, -1.0, 1.0)   # ensure valid range for acos

    theta = acos(costheta)
    if abs(theta) < 0.0001:
        return q2

    sintheta = sqrt(1.0 - costheta * costheta)
    if abs(sintheta) < 0.0001:
        return (q1 + q2) * 0.5

    r1 = sin((1.0 - t) * theta) / sintheta
    r2 = sin(t * theta) / sintheta
    return (q1 * r1) + (q2 * r2)


def slerp_exponential_decay(q1, q2, decay_rate):    # frame-rate independent version of slerp for use in update.
    return slerp(q1, q2, 1 - pow(0.01, decay_rate))


def clamp(value, floor, ceiling):
    return max(min(value, ceiling), floor)


def round_to_closest(value, step=0):
    if not step:
        return value

    step = 1/step
    return round(value * step) / step


def rotate_around_point_2d(point, origin, deg):
    angle_rad = -deg/180 * pi # ursina rotation is positive=clockwise, so do *= -1
    cos_angle = cos(angle_rad)
    sin_angle = sin(angle_rad)
    dx = point[0] - origin[0]
    dy = point[1] - origin[1]

    return (
        origin[0] + (dx*cos_angle - dy*sin_angle),
        origin[1] + (dx*sin_angle + dy*cos_angle)
        )

def world_position_to_screen_position(point): # get screen position(ui space) from world space.
    from ursina import camera, Entity, destroy
    _temp_entity = Entity(position=point, add_to_scene_entities=False)
    result = _temp_entity.screen_position
    destroy(_temp_entity)
    return result


def sum(l):
    try:
        return _sum(l)
    except:
        pass

    total = l[0].__class__()
    for e in l:
        total += e

    return total


def make_gradient(index_value_dict):
    '''
    given a dict of positions and values (usually colors), interpolates the values into a list of with the interpolated values.
    example input: {'0':color.hex('#9d9867'), '38':color.hex('#828131'), '54':color.hex('#5d5b2a'), '255':color.hex('#000000')}
    '''
    min_index = min(int(e) for e in index_value_dict.keys())
    max_index = max(int(e) for e in index_value_dict.keys())
    # default_value = index_value_dict.values()[0]
    # print('-------------', tuple(index_value_dict.values())[0])
    gradient = [None for _ in range(max_index+1-min_index)]

    sorted_dict = [(idx, index_value_dict[str(idx)]) for idx in sorted([int(key) for key in index_value_dict.keys()])]
    # print(sorted_dict)

    for i in range(len(sorted_dict)-1):
        start_index, start_value = sorted_dict[i]
        next_index, next_value = sorted_dict[i+1]
        # print(start_index, '-->', next_index, ':', start_value, '-->', next_value)
        dist = next_index - start_index
        for j in range(dist+1):
            gradient[start_index+j-min_index] = lerp(start_value, next_value, j/dist)

    return gradient

if __name__ == '__main__':
    _test(make_gradient({'0':color.hex('#ff0000ff'), '2':color.hex('#ffffffff')}) == [
        color.hex('#ff0000ff'),
        lerp(color.hex('#ff0000ff'), color.hex('#ffffffff'), .5),
        color.hex('#ffffffff'),
        ])
    _test(make_gradient({'0':color.hex('#ff0000ff'), '4':color.hex('#ffffffff')}) == [
        color.hex('#ff0000ff'),
        lerp(color.hex('#ff0000ff'), color.hex('#ffffffff'), .25),
        lerp(color.hex('#ff0000ff'), color.hex('#ffffffff'), .5),
        lerp(color.hex('#ff0000ff'), color.hex('#ffffffff'), .75),
        color.hex('#ffffffff'),
        ])
    _test(make_gradient({'0':16, '2':0}) == [16, 8, 0])

    _test(make_gradient({'6':0, '8':8}) == [0, 4, 8])


def sample_gradient(list_of_values, t):     # distribute list_of_values equally on a line and get the interpolated value at t (0-1).
    l = len(list_of_values)
    if l == 1:
        return list_of_values[0]

    t *= l-1
    index = floor(t - .001)
    index = clamp(index, 0, l-1)
    relative = t - index
    # print(t, index, relative)

    if index < l-1:
        return lerp(list_of_values[index], list_of_values[index+1], relative)
    else:
        return lerp(list_of_values[index-1], list_of_values[index], relative)



class Bounds:
    __slots__ = ['start', 'end', 'center', 'size']

    def __init__(self, *, start:Vec3=None, end:Vec3=None, center:Vec3=None, size:Vec3=None):
        if start is not None and end is not None:
            self.start = start
            self.end = end
            self.size = end - start
            self.center = start + (self.size * 0.5)

        elif center is not None and size is not None:
            self.center = center
            self.size = size
            half = size * 0.5
            self.start = center - half
            self.end = center + half

        else:
            raise ValueError("Must provide either (start and end) or (center and size)")

    def __repr__(self):
        return f"Bounds(start={self.start}, end={self.end}, center={self.center}, size={self.size})"


if __name__ == '__main__':
    from ursina import *
    from ursinastuff import _test
    app = Ursina()
    e1 = Entity(position = (0,0,0))
    e2 = Entity(position = (0,1,1))
    _test(distance(e1, e2) == 1.4142135623730951)
    _test(distance_2d(Vec2(0,0), Vec2(1,1)) == 1.4142135623730951)

    distance_xz(e1, e2.position)

    between_color = lerp(color.lime, color.magenta, .5)
    print(between_color)
    print(lerp((0,0), (0,1), .5))
    print(lerp(Vec2(0,0), Vec2(0,1), .5))
    print(lerp([0,0], [0,1], .5))

    print(round(Vec3(.38, .1351, 353.26), 2))

    p = (1,0)
    print(p, 'rotated ->', rotate_around_point_2d(p, (0,0), 90))

    app.run()
