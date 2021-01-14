from panda3d.core import Vec2 as PandaVec2




class Vec2(PandaVec2):

    def __round__(self, decimals=4):
        return Vec2(round(self[0], decimals), round(self[1], decimals))


    def __repr__(self):
        return super().__repr__().replace('LVector2f', 'Vec2')


    def __iadd__(self, value):
            for i in range(0, len(value), 2):
                self.add_x(value[i])
                self.add_y(value[i+1])
            return self


    def __add__(self, value):
        return Vec2(self[0]+value[0], self[1]+value[1])


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


    def __mul__(self, value):
        if isinstance(value, (int, float, complex)):
            return Vec2(*(e*value for e in self))

        return Vec2(self[0]*value[0], self[1]*value[1])


    __rmul__ = __mul__



    def __truediv__(self, value):
        if isinstance(value, (int, float, complex)):
            return Vec2(*(e/value for e in self))

        return Vec2(self[0]/value[0], self[1]/value[1])



if __name__ == '__main__':
    a = Vec2(1,1)
    print(a)
    print(round(a))
