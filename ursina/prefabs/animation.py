from ursina import *


class Animation(Sprite):
    def __init__(self, name, fps=12, loop=True, autoplay=True, frame_times=None, **kwargs):

        if isinstance(name, Path):
            texture = load_texture(name.name, name.parent)
        else:
            texture = load_texture(name)

        if texture and texture.path.suffix == '.gif':   # load gif
            import imageio
            from PIL import Image
            path = load_texture(name).path
            gif = imageio.get_reader(path)
            img = Image.open(path)
            img.seek(0)
            frame_times = []
            for i in range(len(gif)):
                img.seek(i)
                frame_times.append(img.info['duration'] / 1000)

            self.frames = [Texture(Image.fromarray(frame)) for frame in gif]

        else:   # load image sequence
            texture_folders = (application.compressed_textures_folder, application.asset_folder, application.internal_textures_folder)
            self.frames = [Texture(e) for e in find_sequence(name, ('png', 'jpg'), texture_folders)]


        if self.frames:
            super().__init__(texture=self.frames[0])

        self.sequence = Sequence(loop=loop, auto_destroy=False)

        self.frame_times = frame_times
        if not self.frame_times:
            self.frame_times = [1/fps for i in range(len(self.frames))]

        for i, frame in enumerate(self.frames):
            self.sequence.append(Func(setattr, self, 'texture', self.frames[i]))
            self.sequence.append(Wait(self.frame_times[i]))

        self.is_playing = False
        self.autoplay = autoplay


        for key, value in kwargs.items():
            setattr(self, key ,value)


        if self.autoplay:
            self.start()


    def start(self):
        if self.is_playing:
            self.finish()
        self.sequence.start()
        self.is_playing = True

    def pause(self):
        self.sequence.pause()

    def resume(self):
        self.sequence.resume()

    def finish(self):
        self.sequence.finish()
        self.is_playing = False


    @property
    def duration(self):     # get the duration of the animation. you can't set it. to do so, change the fps instead.
        return self.sequence.duration


    def __setattr__(self, name, value):
        if hasattr(self, 'frames') and name in ('color', 'origin'):
            for f in self.frames:
                setattr(f, name, value)

        if name == 'loop':
            self.sequence.loop = value

        try:
            super().__setattr__(name, value)
        except Exception as e:
            return e





if __name__ == '__main__':
    # application.asset_folder = application.asset_folder.parent.parent / 'samples'
    app = Ursina()

    '''
    Loads an image sequence as a frame animation.
    So if you have some frames named image_000.png, image_001.png, image_002.png and so on,
    you can load it like this: Animation('image')

    You can also load a .gif by including the file type: Animation('image.gif')
    '''

    Animation('ursina_wink')
    # Animation('city_in_desert_valley_water.gif')

    app.run()
