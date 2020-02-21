from panda3d.core import Vec3 as PandaVec3




class Vec3(PandaVec3):

    def __round__(self, n=3):
        return Vec3(*(round(e,n) for e in self))


    def __str__(self):
        return f'{self.__class__.__name__}({self[0]}, {self[1]}, {self[2]})'

    # def __len__(self):
    #     return 3

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



if __name__ == '__main__':
    a = Vec3(0,0,0)
    b = Vec3(1.252352324,0,1)

    print(b.x)
    b.x += 2
    print(b.x)
    print(round(b))
