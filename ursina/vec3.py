from panda3d.core import Vec3 as PandaVec3
from ursina.vec2 import Vec2
from ursina.scripts.property_generator import generate_properties_for_class


@generate_properties_for_class()
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


    def __neg__(self):
        return Vec3(-self[0], -self[1], -self[2])


    def __sub__(self, value):
        if len(value) == 3:
            return Vec3(self[0]-value[0], self[1]-value[1], self[2]-value[2])

        if len(value) == 2:
            return Vec3(self[0]-value[0], self[1]-value[1], self[2])


    def x_getter(self):
        return self[0]
    def x_setter(self, value):
        self[0] = value

    def y_getter(self):
        return self[1]
    def y_setter(self, value):
        self[1] = value

    def z_getter(self):
        return self[2]
    def z_setter(self, value):
        self[2] = value

    def xy_getter(self):
        return Vec2(self[0], self[1])
    def xy_setter(self, value):
        self[0] = value[0]
        self[1] = value[1]

    def yx_getter(self):
        return Vec2(self[1], self[0])
    def yx_setter(self, value):
        self[1] = value[0]
        self[0] = value[1]

    def xz_getter(self):
        return Vec2(self[0], self[2])
    def xz_setter(self, value):
        self[0] = value[0]
        self[2] = value[1]

    def yz_getter(self):
        return Vec2(self[1], self[2])
    def yz_setter(self, value):
        self[1] = value[0]
        self[2] = value[1]

    def xzy_getter(self):
        return Vec3(self[0], self[2], self[1])
    def xzy_setter(self, value):
        self[0] = value[0]
        self[2] = value[1]
        self[1] = value[2]

    def X_getter(self):    # get x as int
        return int(self.x)
    def Y_getter(self):    # get y as int
        return int(self.y)
    def Z_getter(self):    # get z as int
        return int(self.z)
    def XY_getter(self):
        return Vec2(self.X, self.Y)
    def XZ_getter(self):
        return Vec2(self.X, self.Z)
    def XYZ_getter(self):
        return (self.X, self.Y, self.Z)
    def XZY_getter(self):
        return (self.X, self.Z, self.Y)


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

    test_input = Vec3(1.1, 2.5, 3.4)
    _test(test_input.x_getter, (), 1.1, approximate=True)
    _test(test_input.X_getter, (), 1)
    _test(test_input.y_getter, (), 2.5, approximate=True)
    _test(test_input.Y_getter, (), 2)
    _test(test_input.z_getter, (), 3.4, approximate=True)
    _test(test_input.Z_getter, (), 3)
    _test(test_input.xy_getter, (), Vec2(1.1,2.5))
    _test(test_input.XY_getter, (), Vec2(1,2))
    _test(test_input.xz_getter, (), Vec2(1.1,3.4))
    _test(test_input.XZ_getter, (), Vec2(1,3))