from ursina import *


class Animation(Entity):

    def __init__(self, texture, fps=12, loop=True, autoplay=True, frame_times=None, **kwargs):
        super().__init__()
        self.frames = list()

        for i in range(999):
            frame = Entity(
                parent=self,
                model='quad',
                texture=texture + '_' + str(i).zfill(4),
                name=str(i),
                ignore=True,
                )
            if not frame.texture:
                destroy(frame)
                frame = self.frames[0]
                break

            for key, value in kwargs.items():
                if key.startswith('origin') or key in ('double_sided', 'color'):
                    setattr(frame, key, value)
                if key == 'filtering':
                    setattr(frame.texture, key, value)

            self.frames.append(frame)

        self.scale = (frame.texture.width/100, frame.texture.height/100)
        self.aspect_ratio = self.scale_x / self.scale_y

        self.stop()
        self.sequence = Sequence(loop=loop)

        for i in range(len(self.frames)):
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
    animation = Animation('ursina_wink', fps=2, scale=(-5,5,1), filtering=None, double_sided=True)
    # Entity(model='quad', scale_x=-1, double_sided=True)
    app.run()
