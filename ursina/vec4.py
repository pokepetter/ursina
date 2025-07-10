from panda3d.core import Vec4 as PandaVec4


class Vec4(PandaVec4):

    def __round__(self, decimals=4):
        return Vec4(*(round(e,decimals) for e in self))


    def __repr__(self):
        return f'Vec4({self[0]}, {self[1]}, {self[2]}, {self[3]})'


    def __iadd__(self, value):
        if len(value) % 3 == 0:
            for i in range(0, len(value), 3):
                self.add_x(value[i])
                self.add_y(value[i+1])
                self.add_z(value[i+2])
                return self

        if len(value) % 2 == 0:
            for i in range(0, len(value), 2):
                self.add_x(value[i])
                self.add_y(value[i+1])
            return self


    def __add__(self, value):
        if len(value) == 4:
            return Vec4(self[0]+value[0], self[1]+value[1], self[2]+value[2], self[3]+value[3])

        if len(value) == 3:
            return Vec4(self[0]+value[0], self[1]+value[1], self[2]+value[2], self[3])

        elif len(value) == 2:
            return Vec4(self[0]+value[0], self[1]+value[1], self[2], self[3])



    def __mul__(self, value):
        if isinstance(value, int | float | complex):
            return Vec4(*(e*value for e in self))

        return Vec4(self[0]*value[0], self[1]*value[1], self[2]*value[2], self[3]*value[3])


    __rmul__ = __mul__


    def __truediv__(self, value):
        if isinstance(value, int | float | complex):
            return Vec4(*(e/value for e in self))

        return Vec4(self[0]/value[0], self[1]/value[1], self[2]/value[2], self[3]/value[3])


    def __abs__(self):
        return Vec4(*[abs(e) for e in self])

if __name__ == '__main__':
    from ursina.ursinastuff import _test
    _test(Vec4(1,0,0,0) * 2 == Vec4(2,0,0,0))
    _test(Vec4(1,0,1,1) * Vec4(2,1,2,3) == Vec4(2,0,2,3))

    def _test_Vec4_plus_equal():
        b = Vec4(1.252352324, 0, 1, .2)
        b += Vec4(0,1)
        return b == Vec4(1.252352324, 1, 1, .2)
    _test(_test_Vec4_plus_equal)
