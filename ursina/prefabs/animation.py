"""
animation.py

This file contains the Animation class, which is responsible for handling frame-based animations in the Ursina engine.
It extends the Sprite class and provides functionality to load and play animations from image sequences or GIF files.
"""

from ursina import *


class Animation(Sprite):
    """
    The Animation class is used to create and control frame-based animations.

    Attributes:
        frames (list): A list of Texture objects representing the frames of the animation.
        sequence (Sequence): A Sequence object to manage the animation playback.
        frame_times (list): A list of frame durations in seconds.
        is_playing (bool): A flag indicating whether the animation is currently playing.
        autoplay (bool): A flag indicating whether the animation should start playing automatically.
    """

    def __init__(self, name, fps=12, loop=True, autoplay=True, frame_times=None, **kwargs):
        """
        Initialize the Animation object.

        Args:
            name (str or Path): The name or path of the animation frames or GIF file.
            fps (int, optional): The frames per second for the animation. Defaults to 12.
            loop (bool, optional): Whether the animation should loop. Defaults to True.
            autoplay (bool, optional): Whether the animation should start playing automatically. Defaults to True.
            frame_times (list, optional): A list of frame durations in seconds. Defaults to None.
            **kwargs: Additional keyword arguments to set as attributes.
        """
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
            texture_folders = (application.textures_compressed_folder, application.asset_folder, application.internal_textures_folder)
            self.frames = [Texture(e) for e in find_sequence(name, ('png', 'jpg'), texture_folders)]

        if not self.frames:
            self.frames = [load_texture('white_cube.png')]
        
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
        """
        Start playing the animation.
        """
        if self.is_playing:
            self.finish()
        self.sequence.start()
        self.is_playing = True

    def pause(self):
        """
        Pause the animation.
        """
        self.sequence.pause()

    def resume(self):
        """
        Resume the animation.
        """
        self.sequence.resume()

    def finish(self):
        """
        Finish the animation and stop playing.
        """
        self.sequence.finish()
        self.is_playing = False


    @property
    def duration(self):
        """
        Get the duration of the animation.

        Returns:
            float: The duration of the animation in seconds.
        """
        return self.sequence.duration


    def __setattr__(self, name, value):
        """
        Set an attribute of the Animation object.

        Args:
            name (str): The name of the attribute.
            value: The value to set for the attribute.
        """
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
    Consider using SpriteSheetAnimation instead if possible.
    So if you have some frames named image_000.png, image_001.png, image_002.png and so on,
    you can load it like this: Animation('image')

    You can also load a .gif by including the file type: Animation('image.gif')
    '''

    a = Animation('ursina_wink')
# Animation('city_in_desert_valley_water.gif')

    app.run()
