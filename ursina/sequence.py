from ursina import application
import time


Wait = float


class Func():
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.delay = 0
        self.finished = False

    def __call__ (self):
        self.finished = True
        return self.func(*self.args, **self.kwargs)


class Sequence():
    default_time_step = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = list(args)
        self.t = 0
        self.time_step = Sequence.default_time_step
        self.unscaled = False
        self.duration = 0
        self.funcs = []
        self.started = False
        self.paused = False
        self.ignore_paused = False
        self.loop = False
        self.auto_destroy = False
        self.entity = None  # you can assign this to make the sequence pause when the entity is disabled or .ignore is True

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.generate()
        application.sequences.append(self)



    def generate(self):
        self.funcs = []

        for arg in self.args:
            if isinstance(arg, (int, float)):
                self.duration += arg

            elif isinstance(arg, Func):
                arg.delay = self.duration
                self.funcs.append(arg)

    def __call__(self):
        self.start()
        return self



    def append(self, arg):
        self.args.append(arg)

        if isinstance(arg, (int, float)):
            self.duration += arg

        elif callable(arg):
            arg.delay = self.duration
            self.funcs.append(arg)

        else:
            raise TypeError(f'Invalid type: {arg}. Must be Func, Wait or float.')


    def extend(self, list):
        for e in list:
            self.append(e)


    def start(self):
        for f in self.funcs:
            f.finished = False

        self.t = 0
        self.started = True
        self.paused = False
        return self

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def finish(self):
        self.t = self.duration
        self.update()
        self.paused = False
        self.started = False

    def kill(self):
        if self in application.sequences:
            application.sequences.remove(self)
            del self

    @property
    def finished(self):
        return self.t >= self.duration


    def update(self):
        if not self.started:
            return

        if self.ignore_paused is False and (self.paused or application.paused):
            return

        if self.entity and (not self.entity.enabled or self.entity.ignore):
            return


        if self.time_step is None:
            if not self.unscaled:
                self.t += time.dt
            else:
                self.t += time.dt_unscaled
        else:
            self.t += self.time_step

        for f in self.funcs:
            if not f.finished and f.delay <= self.t:
                f()


        if self.t >= self.duration:
            if self.loop:
                for f in self.funcs:
                    f.finished = False

                if time.dt > self.duration: # if delta time is too big, set t to 0 so it doesn't get stuck, but allow desync.
                    self.t = 0
                else:
                    self.t -= self.duration
                return

            if self.auto_destroy and self in application.sequences:
                application.sequences.remove(self)
                del self



if __name__ == '__main__':
    from ursina import *
    from ursina import Ursina, Entity
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
