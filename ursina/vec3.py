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

        elif len(value) == 2:
            return Vec3(self[0]+value[0], self[1]+value[1], self[2])


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
        return Vec2(self.x, self.y)
    @xy.setter
    def xy(self, value):
        self[0] = value[0]
        self[1] = value[1]

    @property
    def xz(self):
        return Vec2(self.x, self.z)
    @xz.setter
    def xz(self, value):
        self[0] = value[0]
        self[2] = value[1]

    @property
    def yz(self):
        return Vec2(self.y, self.z)
    @yz.setter
    def yz(self, value):
        self[1] = value[0]
        self[2] = value[1]




    def __mul__(self, value):
        if isinstance(value, (int, float, complex)):
            return Vec3(*(e*value for e in self))

        return Vec3(self[0]*value[0], self[1]*value[1], self[2]*value[2])


    __rmul__ = __mul__


    def __truediv__(self, value):
        if isinstance(value, (int, float, complex)):
            return Vec3(*(e/value for e in self))

        return Vec3(self[0]/value[0], self[1]/value[1], self[2]/value[2])


if __name__ == '__main__':
    a = Vec3(1,0,0) * 2
    a = Vec3(1,0,1) * Vec3(2,1,2)
    b = Vec3(1.252352324,0,1)
    b += Vec3(0,1)

    # test
    print(a)
    b.x += 2
    print(b.x)
    print('xy:', b.xy)
    print(round(b))
    print(round(b.xy))
    print('-----------', a * 2)
    print('-----------', 2 * a)
