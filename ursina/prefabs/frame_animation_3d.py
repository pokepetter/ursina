from ursina import *


class FrameAnimation3d(Entity):
    def __init__(self, name, fps=12, loop=True, autoplay=True, frame_times=None, **kwargs):
        super().__init__()

        model_folders = [application.compressed_models_folder, application.asset_folder]
        model_names = find_sequence(name, ('*',), folders=model_folders)
        if not model_names:
            if application.raise_exception_on_missing_model:
                raise FileNotFoundError(f'error: could not find models starting with: {name}')
            self.frames = []
            return

        self.frames = [Entity(parent=self, model=e.stem, enabled=False, add_to_scene_entities=False) for e in model_names]
        self.frames[0].enabled = True

        self.sequence = Sequence(loop=loop, auto_destroy=False)
        for i, frame in enumerate(self.frames):
            self.sequence.append(Func(setattr, self.frames[i-1], 'enabled', False))
            self.sequence.append(Func(setattr, self.frames[i], 'enabled', True))
            self.sequence.append(Wait(1/fps))

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


    def __setattr__(self, name, value):
        if hasattr(self, 'frames') and name in ('color', 'origin', 'texture'):
            for f in self.frames:
                setattr(f, name, value)

        if name == 'loop':
            self.sequence.loop = value

        try:
            super().__setattr__(name, value)
        except Exception as e:
            return e


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
