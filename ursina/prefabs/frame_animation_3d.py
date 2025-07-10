from ursina import *


class FrameAnimation3d(Entity):
    def __init__(self, name, fps=12, loop=True, autoplay=True, frame_times=None, auto_destroy=False, **kwargs):
        super().__init__(name=name)
        self.play = self.start

        model_folders = (application.models_compressed_folder, application.asset_folder)
        model_names = find_sequence(name, ('*',), folders=model_folders)
        if not model_names:
            if application.raise_exception_on_missing_model:
                raise FileNotFoundError(f'error: could not find models starting with: {name}')
            self.frames = []
            self.sequence = Sequence(loop=loop, auto_destroy=auto_destroy)
            return

        self.frames = [Entity(parent=self, model=e.stem, enabled=False) for e in model_names]
        self.frames[0].enabled = True

        self.sequence = Sequence(loop=loop, auto_destroy=auto_destroy)
        for i, _frame in enumerate(self.frames):
            self.sequence.append(Func(setattr, self.frames[i-1], 'enabled', False))
            self.sequence.append(Func(setattr, self.frames[i], 'enabled', True))
            self.sequence.append(Wait(1/fps))

        if loop == 'boomerang':
            for i in range(len(self.frames)-1, 0, -1):
                self.sequence.append(Func(setattr, self.frames[i], 'enabled', False))
                self.sequence.append(Func(setattr, self.frames[i-1], 'enabled', True))
                self.sequence.append(Wait(1/fps))

        if auto_destroy:
            self.sequence.append(Func(destroy, self))

        self.autoplay = autoplay

        for key, value in kwargs.items():
            setattr(self, key ,value)

        if self.autoplay:
            self.start()


    def start(self):
        if not self.sequence.finished:
            self.sequence.finish()
        self.sequence.start()

    def pause(self):
        self.sequence.pause()

    def resume(self):
        self.sequence.resume()

    def finish(self):
        self.sequence.finish()


    @property
    def duration(self):
        return self.sequence.duration


    @property
    def current_frame(self):
        for e in self.frames:
            if e.enabled:
                return e


    def __setattr__(self, name, value):
        if hasattr(self, 'frames') and name in ('shader', 'color', 'origin', 'texture', 'texture_scale', 'texture_offset'):
            for f in self.frames:
                setattr(f, name, value)

        if name == 'loop':
            self.sequence.loop = value

        try:
            super().__setattr__(name, value)
        except Exception as e:
            return e

    def on_destroy(self):
        self.sequence.kill()



if __name__ == '__main__':
    application.asset_folder = application.asset_folder.parent.parent / 'samples'
    app = Ursina()

    '''
    Loads an obj sequence as a frame animation.
    So if you have some frames named run_cycle_000.obj, run_cycle_001.obj, run_cycle_002.obj and so on,
    you can load it like this: FrameAnimation3d('run_cycle_')
    '''

    FrameAnimation3d('blob_animation_')

    # test
    EditorCamera()

    app.run()
