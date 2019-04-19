from ursina import *
import math
from ursina import application
import time


class Wait():
    def __init__(self, duration):
        self.duration = duration


class Func():
    def __init__(self, func, *args):
        self.func = func
        self.args = args


class Sequence():
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = list(args)
        self.t = 0
        self.funcs = list()
        self.paused = True
        self.loop = False

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.generate()
        application.sequences.append(self)



    def generate(self):
        self.funcs = list()
        n = 0
        for arg in self.args:
            if isinstance(arg, Wait):
                n += arg.duration
            elif isinstance(arg, (int, float)):
                n += arg

            elif isinstance(arg, Func):
                self.funcs.append([arg.func, arg.args, n])


    def append(self, item):
        self.args.append(item)
        self.generate()


    def start(self):
        self.t = 0
        self.paused = False

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def finish(self):
        self.t = math.inf
        self.paused = False


    def update(self):
        if self.paused:
            return

        self.t += time.dt * application.time_scale

        for f in self.funcs:
            if f[2] > -.1 and f[2] <= self.t:
                # print('run:', f[0], 'after:', self.t)
                f[0](*f[1])
                f[2] = -1


        if self.t >= self.funcs[len(self.funcs)-1][2]:
            if self.loop:
                self.t = 0
                return
            # print('finish')
            application.sequences.remove(self)
            del self


def test(arg=''):
    print('yolo', arg)

if __name__ == '__main__':
    app = Ursina()
    s = Sequence(
        1,
        Func(test),
        1,
        Func(test),
        1,
        Func(test),
        2,
        Func(test, 'awdwkdmwd'),
        2,
        loop=True
    )
    # application.sequences.append(s)
    def input(key):
        if key == 's':
            s.start()
        if key == 'f':
            s.finish()
        if key == 'p':
            s.pause()
        if key == 'r':
            s.resume()


    app.run()
