from panda3d.core import Vec2 as PandaVec2
from ursina.scripts.property_generator import generate_properties_for_class


@generate_properties_for_class()
class Vec2(PandaVec2):
    def __round__(self, decimals=4):
        return type(self)(round(self[0], decimals), round(self[1], decimals))


    def __repr__(self):
        return f'{self.__class__.__name__}({self.x},{self.y})'


    def __iadd__(self, value):
            for i in range(0, len(value), 2):
                self.add_x(value[i])
                self.add_y(value[i+1])
            return self


    def __add__(self, value):
        return type(self)(self[0]+value[0], self[1]+value[1])


    def __sub__(self, value):
        return type(self)(self[0]-value[0], self[1]-value[1])


    def x_getter(self):
        return self[0]
    def x_setter(self, value):
        self[0] = value

    def y_getter(self):
        return self[1]
    def y(self, value):
        self[1] = value

    def yx_getter(self):
        return type(self)(self.y, self.x)
    def yx_setter(self, value):
        self[1] = value[0]
        self[0] = value[1]

    def x_y_getter(self):
        from ursina.vec3 import Vec3
        return Vec3(self[0], 0, self[1])

    def X_getter(self):    # get x as int
        return int(self.x)
    def Y_getter(self):    # get y as int
        return int(self.y)
    def XY_getter(self):
        return (self.X, self.Y)



    def __mul__(self, value):
        if isinstance(value, (int, float, complex)):
            return type(self)(*(e*value for e in self))

        return type(self)(self[0]*value[0], self[1]*value[1])


    __rmul__ = __mul__



    def __truediv__(self, value):
        if isinstance(value, (int, float, complex)):
            return type(self)(*(e/value for e in self))

        return type(self)(self[0]/value[0], self[1]/value[1])


    def __abs__(self):
        return type(self)(*[abs(e) for e in self])


class IntVec2(Vec2):
    def __init__(self, x=0, y=0):
        super().__init__(int(x), int(y))

Vec2.zero = Vec2(0,0)
Vec2.one = Vec2(1,1)
Vec2.right = Vec2(1,0)
Vec2.left = Vec2(-1,0)
Vec2.up = Vec2(0,1)
Vec2.down = Vec2(0,-1)

Vec2.cardinal_directions = (Vec2.up, Vec2.right, Vec2.down, Vec2.left)
Vec2.ordinal_directions = (Vec2(1,1), Vec2(1,-1), Vec2(-1,-1), Vec2(-1,1))
Vec2.compass_directions = (Vec2(0,1), Vec2(1,1), Vec2(1,0), Vec2(1,-1), Vec2(0,-1), Vec2(-1,-1), Vec2(-1,0), Vec2(-1,1))



if __name__ == '__main__':
    from ursina.ursinastuff import _test
    a = Vec2(1,1)
    print(a)
    print(round(a))

    _test(IntVec2(0,0) + Vec2(1,2) == IntVec2(1,2)) # passes
    _test(IntVec2(0,0) + Vec2(1,2) != Vec2(1,2))    # fails

    print(a.x_y)