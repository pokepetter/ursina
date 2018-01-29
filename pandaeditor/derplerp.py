from pandaeditor import *

# def derplerp(var, target_value, duration, curve='linear'):
#     # print(var, target_value)
#     var = target_value

# class Test():
#     pass
import time

def move_x(entity, value, duration=0, curve='linear', steps=10):
    if duration == 0:
        entity.x = value
        return
    for i in range(steps):
        entity.x = entity.x + (value / steps)
        time.sleep(duration / steps)
        print(entity.x)

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
