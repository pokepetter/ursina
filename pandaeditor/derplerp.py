from pandaeditor import *

def move(entity, value, duration=.1, curve='linear'):
    s = Sequence(entity.posInterval(duration, Point3(value[0], value[2], value[1])))
    s.start()
    return s

def move_x(entity, value, duration=.1, curve='linear'):
    s = Sequence(entity.posInterval(duration, Point3(value, entity.z, entity.y)))
    s.start()
    return s

def move_y(entity, value, duration=.1, curve='linear'):
    s = Sequence(entity.posInterval(duration, Point3(entity.x, entity.z, value)))
    s.start()
    return s

def move_z(entity, value, duration=.1, curve='linear'):
    s = Sequence(entity.posInterval(duration, Point3(entity.x, value, entity.y)))
    s.start()
    return s


def scale(entity, value, duration=.1, curve='linear'):
    s = Sequence(entity.scaleInterval(duration, Vec3(value[0], value[2], value[1])))
    s.start()
    return s

def scale_x(entity, value, duration=.1, curve='linear'):
    s = Sequence(entity.scaleInterval(duration, Vec3(value, entity.scale_z, entity.scale_y)))
    s.start()
    return s

def scale_y(entity, value, duration=.1, curve='linear'):
    s = Sequence(entity.scaleInterval(duration, Vec3(entity.scale_x, entity.scale_z, value)))
    s.start()
    return s

def scale_z(entity, value, duration=.1, curve='linear'):
    s = Sequence(entity.scaleInterval(duration, Vec3(entity.scale_x, value, entity.scale_y)))
    s.start()
    return s


class Test(Entity):

    def input(self, key):
        if key == 'space':
            print('start lerp')
            move_x(e, 5, 1)


if __name__ == '__main__':
    # test = Test()
    # test.a = 0
    # derplerp(test.a, 1, 1)
    # print(test.a)
    app = PandaEditor()
    e = Entity()
    e.model = 'cube'
    e.color = color.green
    test = Test()
    app.run()
    # move_x(e, 3, 1)
    # print(e.x)
