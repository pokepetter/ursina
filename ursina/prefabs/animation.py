from ursina import *
# from direct.interval.IntervalGlobal import Sequence, Func, Wait, SoundInterval

class Animation(Entity):

    def __init__(self, texture, fps=12, loop=True, autoplay=True, frame_times=None, **kwargs):
        super().__init__()
        self.frames = list()

        for i in range(999):
            sprite = Sprite(
                texture + '_' + str(i).zfill(4),
                parent=self,
                name=str(i),
                add_to_scene=False
                )
            if not sprite:
                break

            if 'double_sided' in kwargs:
                sprite.double_sided = kwargs['double_sided']

            self.frames.append(sprite)
            # print(sprite)

        self.stop()
        self.sequence = Sequence(loop=loop)

        for i in range(len(self.frames)):
            # self.sequence.append(Func(print, self.frames[i]))
            self.sequence.append(Func(self.stop))
            self.sequence.append(Func(setattr, self.frames[i], 'enabled', True))
            self.sequence.append(Wait(1/fps))

        if autoplay:
            self.play()

        for key, value in kwargs.items():
            setattr(self, key, value)


    def play(self):
        self.stop()
        self.sequence.start()


    def stop(self):
        for frame in self.frames:
            frame.enabled = False


    def __setattr__(self, name, value):
        if hasattr(self, 'frames') and name in ('color', 'origin'):
            for f in self.frames:
                setattr(f, name, value)

        try:
            super().__setattr__(name, value)
        except Exception as e:
            return e




if __name__ == '__main__':
    app = Ursina()
    animation = Animation('catlike_creature_run', fps=1/4)
    app.run()
