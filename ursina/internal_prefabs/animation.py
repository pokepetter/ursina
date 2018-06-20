from ursina import *

class Animation(Entity):

    def __init__(self, texture, fps=12, frame_times=None):
        super().__init__()
        self.frames = list()
        self.autoplay = True

        for i in range(999):
            sprite = Sprite(
                texture + '_' + str(i).zfill(4),
                parent=self,
                name=str(i),
                )
            if not sprite:
                break
            self.frames.append(sprite)

        self.stop()
        self.sequence = Sequence()
        for i in range(len(self.frames)):
            # self.sequence.append(Func(print, self.frames[i]))
            self.sequence.append(Func(self.stop))
            self.sequence.append(Func(setattr, self.frames[i], 'enabled', True))
            self.sequence.append(Wait(1/8))

        if self.autoplay:
            self.play()

    def play(self):
        self.stop()
        self.sequence.loop()


    def stop(self):
        for frame in self.frames:
            frame.enabled = False


if __name__ == '__main__':
    app = ursina()
    animation = Animation('catlike_creature_run')
    app.run()
