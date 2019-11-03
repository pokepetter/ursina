from ursina import *
import math
from ursina import application
import time


class Wait():
    def __init__(self, duration):
        self.duration = duration


class Func():
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs


class Sequence():

    default_time_step = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = list(args)
        self.t = 0
        self.time_step = Sequence.default_time_step
        self.duration = 0
        self.funcs = list()
        self.paused = True
        self.loop = False
        self.auto_destroy = True

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.generate()
        application.sequences.append(self)



    def generate(self):
        self.funcs = list()

        for arg in self.args:
            if isinstance(arg, Wait):
                self.duration += arg.duration
            elif isinstance(arg, (int, float)):
                self.duration += arg

            elif isinstance(arg, Func):
                self.funcs.append([arg.func, arg.args, arg.kwargs, self.duration, False])


    def append(self, arg):
        self.args.append(arg)

        if isinstance(arg, Wait):
            self.duration += arg.duration
        elif isinstance(arg, (int, float)):
            self.duration += arg

        elif isinstance(arg, Func):
            self.funcs.append([arg.func, arg.args, arg.kwargs, self.duration, False])


    def start(self):
        for f in self.funcs:
            f[4] = False

        self.t = 0
        self.paused = False

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def finish(self):
        self.t = math.inf
        self.paused = False
        self.update()

    def kill(self):
        if self.auto_destroy and self in application.sequences:
            application.sequences.remove(self)
            del self

    def update(self):
        if self.paused:
            return

        if self.time_step is None:
            self.t += time.dt * application.time_scale
        else:
            self.t += self.time_step * application.time_scale

        for f in self.funcs:
            func, args, kwargs, when, finished = f
            if not finished and when <= self.t:
                # print('run:', f[0], 'after:', self.t)
                func(*args, **kwargs)
                f[4] = True


        if self.t >= self.duration:
            if self.loop:
                for f in self.funcs:
                    f[4] = False # set has run to False again

                self.t = 0
                return
            # print('finish')
            if self.auto_destroy and self in application.sequences:
                application.sequences.remove(self)
                del self



if __name__ == '__main__':

    app = Ursina()
    e = Entity(model='quad')
    s = Sequence(
        1,
        Func(print, 'one'),
        Func(e.fade_out, duration=1),
        1,
        Func(print, 'two'),
        Func(e.fade_in, duration=1),
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
