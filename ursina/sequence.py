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
        self.duration = 0
        self.funcs = list()
        self.paused = True
        self.loop = False

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.generate()
        application.sequences.append(self)



    def generate(self):
        self.funcs = list()
        # self.duration = 0
        for arg in self.args:
            if isinstance(arg, Wait):
                self.duration += arg.duration
            elif isinstance(arg, (int, float)):
                self.duration += arg

            elif isinstance(arg, Func):
                self.funcs.append([arg.func, arg.args, self.duration])


    def append(self, arg):
        self.args.append(arg)

        if isinstance(arg, Wait):
            self.duration += arg.duration
        elif isinstance(arg, (int, float)):
            self.duration += arg

        elif isinstance(arg, Func):
            self.funcs.append([arg.func, arg.args, self.duration])
        # self.generate()


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



if __name__ == '__main__':

    app = Ursina()
    s = Sequence(
        1,
        Func(print, 'one'),
        1,
        Func(print, 'two'),
        loop=True
        )

    s.append(
        Func(print, 'appended to sequence')
        )

    def input(key):
        actions = {'s' : s.start, 'f' : s.finish, 'p' : s.pause, 'r' : s.resume}
        if key in actions:
            actions[key]()


    app.run()
