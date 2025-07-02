from ursina import application
import time


Wait = float


class Func:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__ (self):
        return self.func(*self.args, **self.kwargs)


class Sequence:
    default_time_step = None

    def __init__(self, *args, unscaled=False, started=False, ignore_paused=False, loop=False, auto_destroy=False, entity=None, time_scale=1, name='sequence', **kwargs):
        super().__init__()
        self.args = list(args)
        self.t = 0
        self.time_step = Sequence.default_time_step
        self.time_scale = time_scale
        self.duration = 0
        self.funcs = []
        self.func_call_time = []
        self.func_finished_statuses = []
        self.unscaled = unscaled
        self.paused = False
        self.name = name
        self.entity = entity  # you can assign this to make the sequence pause when the entity is disabled or .ignore is True
        self.ignore_paused = ignore_paused
        self.loop = loop
        self.auto_destroy = auto_destroy
        self.started = started

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.generate()
        application.sequences.append(self)


    def generate(self):
        self.duration = 0
        self.funcs = []
        self.func_call_time = []
        self.func_finished_statuses = []

        for arg in self.args:
            if isinstance(arg, (int, float)):
                self.duration += arg

            elif callable(arg):
                self.funcs.append(arg)
                self.func_call_time.append(self.duration)
                self.func_finished_statuses.append(False)

        # print('-----------')
    def __str__(self):
        return '\n'.join([str(e) for e in zip(self.funcs, self.func_call_time, self.func_finished_statuses)])

    def __call__(self):
        self.start()
        return self


    def append(self, arg, regenerate=True):
        # print('---------------', arg, callable(arg))
        if not callable(arg) and not isinstance(arg, (int, float)):
            raise TypeError(f'Invalid type: {arg}. Must be callable, Func, Wait or float.')

        self.args.append(arg)
        if regenerate:
            self.generate()

    def extend(self, list):
        for e in list:
            self.append(e, regenerate=False)
        self.generate()

    def start(self):
        for i, f in enumerate(self.funcs):
            self.func_finished_statuses[i] = False

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
                self.t += time.dt * self.time_scale
            else:
                self.t += time.dt_unscaled
        else:
            self.t += self.time_step

        for i, f in enumerate(self.funcs):
            if not self.func_finished_statuses[i] and self.func_call_time[i] <= self.t:
                f()
                self.func_finished_statuses[i] = True


        if self.t >= self.duration:
            if self.loop:
                for i, f in enumerate(self.funcs):
                    self.func_finished_statuses[i] = False

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
    def some_func():
        print('some_func')

    s = Sequence(
        some_func,
        1,
        Func(print, 'one'),
        Func(e.fade_out, duration=1),
        Wait(1),
        loop=True
        )

    for i in range(8):
        s.append(Func(print, i))
        s.append(Wait(.2))

    print(s)

    def input(key):
        actions = {'s' : s.start, 'f' : s.finish, 'p' : s.pause, 'r' : s.resume}
        if key in actions:
            actions[key]()

    app.run()
