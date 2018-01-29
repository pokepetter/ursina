from pandaeditor import *


def move_x(entity, value, duration=0, curve='linear'):
    s = Sequence(entity.posInterval(duration, Point3(value, entity.z, entity.y)))
    s.start()

def move_y(entity, value, duration=0, curve='linear'):
    s = Sequence(entity.posInterval(duration, Point3(entity.x, entity.z, value)))
    s.start()


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
