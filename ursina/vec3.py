from panda3d.core import Vec3 as PandaVec3
from ursina.vec2 import Vec2



class Vec3(PandaVec3):
    def __round__(self, decimals=4):
        return Vec3(*(round(e,decimals) for e in self))


    def __repr__(self):
        return super().__repr__().replace('LVector3f', 'Vec3')


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
        if len(value) == 3:
            return Vec3(self[0]+value[0], self[1]+value[1], self[2]+value[2])

        if len(value) == 2:
            return Vec3(self[0]+value[0], self[1]+value[1], self[2])


    def __sub__(self, value):
        if len(value) == 3:
            return Vec3(self[0]-value[0], self[1]-value[1], self[2]-value[2])

        if len(value) == 2:
            return Vec3(self[0]-value[0], self[1]-value[1], self[2])


    @property
    def x(self):
        return self[0]
    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        return self[1]
    @y.setter
    def y(self, value):
        self[1] = value

    @property
    def z(self):
        return self[2]
    @z.setter
    def z(self, value):
        self[2] = value

    @property
    def xy(self):
        return Vec2(self[0], self[1])
    @xy.setter
    def xy(self, value):
        self[0] = value[0]
        self[1] = value[1]

    @property
    def yx(self):
        return Vec2(self[1], self[0])
    @yx.setter
    def yx(self, value):
        self[1] = value[0]
        self[0] = value[1]

    @property
    def xz(self):
        return Vec2(self[0], self[2])
    @xz.setter
    def xz(self, value):
        self[0] = value[0]
        self[2] = value[1]

    @property
    def yz(self):
        return Vec2(self[1], self[2])
    @yz.setter
    def yz(self, value):
        self[1] = value[0]
        self[2] = value[1]

    @property
    def xzy(self):
        return Vec3(self[0], self[2], self[1])
    @xzy.setter
    def xzy(self, value):
        self[0] = value[0]
        self[2] = value[1]
        self[1] = value[2]

    @property
    def X(self):    # get x as int
        return int(self.x)
    @property
    def Y(self):    # get y as int
        return int(self.y)
    @property
    def Z(self):    # get z as int
        return int(self.z)
    @property
    def XY(self):
        return (self.X, self.Y)
    @property
    def XZ(self):
        return (self.X, self.Z)


    def __mul__(self, value):
        if isinstance(value, (int, float, complex)):
            return Vec3(*(e*value for e in self))

        return Vec3(self[0]*value[0], self[1]*value[1], self[2]* (value[2] if len(value) > 2 else 1))


    __rmul__ = __mul__


    def __truediv__(self, value):
        if isinstance(value, (int, float, complex)):
            return Vec3(*(e/value for e in self))

        return Vec3(self[0]/value[0], self[1]/value[1], self[2]/value[2])

    def __abs__(self):
        return Vec3(*[abs(e) for e in self])


Vec3.zero = Vec3(0,0,0)
Vec3.one = Vec3(1,1,1)
Vec3.right = Vec3(1,0,0)
Vec3.left = Vec3(-1,0,0)
Vec3.up = Vec3(0,1,0)
Vec3.down = Vec3(0,-1,0)
Vec3.forward = Vec3(0,0,1)
Vec3.back = Vec3(0,0,-1)


if __name__ == '__main__':
    from ursinastuff import _assert, _test
    _assert(Vec3(1,0,-1) * 2 == Vec3(2,0,-2), name='Vec3*int')
    _assert(Vec3(1,0,-1) * Vec3(1,2,3) == Vec3(1,0,-3), name='Vec3*Vec3')

    b = Vec3(1,0,1)
    b += Vec3(0,1,0)
    _assert(b == Vec3(1,1,1), name='Vec3+=Vec3')

    b = Vec3(0,0,0)
    b.x += 1
    b.y += 1
    b.z += 1
    _assert(b == Vec3(1,1,1), name='Vec3.x+=int')

    _test(round, (Vec3(1.14,2.86,1.25), 0), expected_result=Vec3(1,3,1))
    _test(abs, (Vec3(1,-2,-3), ), expected_result=Vec3(1,2,3))


    # print(round(b))
    # test
    # b.x += 2
    # print(b.x)
    # print('xy:', b.xy)
    # print(round(b.xy))
    # print('-----------', a * 2)
    # print('-----------', 2 * a)
    # print(abs(Vec3(-1,2,-3)))

    # print(Vec3(1,1,1) * (2,2))
