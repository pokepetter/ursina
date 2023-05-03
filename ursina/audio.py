from ursina import application
import random
from ursina.entity import Entity
from ursina import curve
from ursina.ursinastuff import invoke
from ursina.ursinastuff import destroy as _destroy
import panda3d

from panda3d.core import Filename

from typing import Union


class Audio(Entity):

    volume_multiplier = .5  #

    def __init__(self, sound_file_name='', autoplay=True, auto_destroy=False, **kwargs):
        """Plays a sound file. If no sound_file_name is given, it will only create an Audio object that can be used to play sounds.

        Args:
            sound_file_name (str, optional): The name of the sound file.. Defaults to ''.
            autoplay (bool, optional): Whether or not to play on init. Defaults to True.
            auto_destroy (bool, optional): Whether or not to destroy after audio finishes. Defaults to False.
        """
        super().__init__(**kwargs)
        # printvar(sound_file_name)
        if sound_file_name:
            self.clip = sound_file_name
        else:
            self.clip = None

        self.volume = 1
        self.pitch = 1
        self.balance = 0

        self.loop = False
        self.loops = 1
        self.autoplay = autoplay
        self.auto_destroy = auto_destroy

        # self.volume_variation = 0
        # self.pitch_variation = 0

        for key, value in kwargs.items():
            setattr(self, key, value)

        if autoplay:
            self.play()

        if auto_destroy:
            invoke(self.stop, destroy=True, delay=self.length)


    def __setattr__(self, name, value):
        if hasattr(self, 'clip') and self._clip:
            if name == 'volume':
                self._clip.setVolume(value * Audio.volume_multiplier)

            if name == 'pitch':
                self._clip.setPlayRate(value)

            if name == 'loop':
                self._clip.setLoop(value)

            if name == 'loops':
                self._clip.setLoopCount(value)

        try:
            super().__setattr__(name, value)
        except Exception as e:
            return e

    @property
    def clip(self):
        return self._clip

    @clip.setter
    def clip(self, value: Union[str, None]):
        """Sets the audio clip to play.

        Args:
            value (Union[str, panda3d.core.AudioSound]): The name of the audio file or the audio clip itself.
        """
        if isinstance(value, str):
            self.name = value

            if '.' in value:
                file_types = ('',)
            else:
                file_types = ('.ogg', '.wav')

            for folder in (application.asset_folder, application.internal_audio_folder):
                for suffix in file_types:
                    for f in folder.glob(f'**/{value}{suffix}'):
                        p = str(f.resolve())
                        p = Filename.fromOsSpecific(p)
                        self._clip = loader.loadSfx(p)  # type: ignore
                        # print('...loaded audio clip:', f, p)
                        return

            self._clip = None
            print('no audio found with name:', value, 'supported formats: .ogg, .wav')
            return
        else:
            try:
                self._clip = value
            except Exception as e:
                print('no audio found with name:', value, 'supported formats: .ogg, .wav', e)


    @property
    def length(self):     
        """Get the duration of the audio clip."""
        return self.clip.length() if self.clip else 0

    @property
    def status(self):
        """Get the status of the audio clip.

        Returns:
            @property: The status of the audio clip.
        """
        if self.clip:
            return self.clip.status()

    @property
    def ready(self):
        """Get whether or not the audio clip is ready to play.

        Returns:
            int: 1 if ready, 0 if not.
        """
        return 1 if self.clip and self.status > 0 else 0

    @property
    def playing(self):
        """Get whether or not the audio clip is playing.

        Returns:
            int: 1 if playing, 0 if not.
        """
        return 1 if self.clip and self.status == 2 else 0

    @property
    def time(self):
        """Get the current time of the audio clip.

        Returns:
            float: The current time of the audio clip.
        """
        return self.clip.get_time()

    @time.setter
    def time(self, value):
        self.clip.set_time(value)

    @property
    def balance(self):      # pan the audio. should be a value between -.5 and .5. default: 0
        """Get the balance of the audio clip."""
        return self._balance

    @balance.setter
    def balance(self, value):
        """Set the balance of the audio clip."""
        self._balance = value
        self.clip.setBalance(value*2)


    def play(self, start=0):
        """Play the audio clip.
        
        Args:
            start (int, optional): The time to start playing from. Defaults to 0.
        """
        if hasattr(self, 'clip') and self.clip:
            # print('play from:', start)
            self.time = start
            self.clip.play()
        else:
            print(self, 'has no audio clip')

    def pause(self):
        """Pause the audio clip."""
        if self.clip:
            self.paused_volume = self.volume
            self.paused_pitch = self.pitch
            self.paused_balance = self.balance
            self.temp_time = self.time
            self.pitch = 0
            self.stop(destroy=False)

    def resume(self):
        """Resume the audio clip."""
        if self.clip and hasattr(self, 'temp_time'):
            self.clip = self.name
            self.volume = self.paused_volume
            self.pitch = self.paused_pitch
            self.balance = self.paused_balance
            self.play(self.temp_time)

    def stop(self, destroy=True):
        """Stop the audio clip.

        Args:
            destroy (bool, optional): Whether or not to destroy the audio clip once stopped. Defaults to True.
        """
        if self.clip:
            self.clip.stop()
        if destroy:
            _destroy(self)

    def fade(self, value, duration=.5, delay=0, curve=curve.in_expo, resolution=None, interrupt=True):
        """Fade the audio clip to a volume.

        Args:
            value (float): The volume to fade to.
            duration (float, optional): The duration of the fade. Defaults to .5.
            delay (int, optional): The delay before the fade starts. Defaults to 0.
            curve (function, optional): The curve of the fade. Defaults to curve.in_expo.
            resolution (int, optional): The resolution of the fade. Defaults to None.
            interrupt (bool, optional): Whether or not to interrupt the fade. Defaults to True.
        """
        self.animate('volume', value, duration, delay, curve, resolution, interrupt)

    def fade_in(self, value=1, duration=.5, delay=0, curve=curve.in_expo, resolution=None, interrupt='finish',
                destroy_on_ended=False):
        """Fade the audio clip in.
        
        Args:
            value (float, optional): The volume to fade to. Defaults to 1.
            duration (float, optional): The duration of the fade. Defaults to .5.
            delay (int, optional): The delay before the fade starts. Defaults to 0.
            curve (function, optional): The curve of the fade. Defaults to curve.in_expo.
            resolution (int, optional): The resolution of the fade. Defaults to None.
            interrupt (bool, optional): Whether or not to interrupt the fade. Defaults to True.
            destroy_on_ended (bool, optional): Whether or not to destroy the audio clip once the fade is finished. Defaults to False.
        """
        if duration <= 0:
            self.volume = value
        else:
            self.animate('volume', value, duration=duration, delay=delay, curve=curve, resolution=resolution, interrupt=interrupt)
        if destroy_on_ended:
            _destroy(self, delay=duration + .01)

    def fade_out(self, value=0, duration=.5, delay=0, curve=curve.in_expo, resolution=None, interrupt='finish',
                 destroy_on_ended=True):
        """Fade the audio clip out.
        
        Args:
            value (float, optional): The volume to fade to. Defaults to 0.
            duration (float, optional): The duration of the fade. Defaults to .5.
            delay (int, optional): The delay before the fade starts. Defaults to 0.
            curve (function, optional): The curve of the fade. Defaults to curve.in_expo.
            resolution (int, optional): The resolution of the fade. Defaults to None.
            interrupt (bool, optional): Whether or not to interrupt the fade. Defaults to True.
            destroy_on_ended (bool, optional): Whether or not to destroy the audio clip once the fade is finished. Defaults to True.
        """
        if duration <= 0:
            self.volume = value
        else:
            self.animate('volume', value, duration=duration, delay=delay, curve=curve, resolution=resolution, interrupt=interrupt)
        if destroy_on_ended:
            _destroy(self, delay=duration + .05)


if __name__ == '__main__':
    from ursina import Ursina, printvar

    app = Ursina()
    # a = Audio('life_is_currency_wav', pitch=1)
    def input(key):
        if key == 'space':
            a = Audio('life_is_currency', pitch=random.uniform(.5,1), loop=True, autoplay=True)
    # print(a.clip)
    # a.volume=0
    # b = Audio(a.clip)
    # a2 = Audio(clip=a.clip)
    # a2 = duplicate(a)
    # a2.clip = a.clip
    # a2.play()
    # print(a2.clip)
    # a.fade_out(delay=1)
    # DebugMenu(a)

    # def input(key):
    #     if key == 'f':
    #         a.fade_out(duration=4, curve=curve.linear)
    #
    # def update():
    #     print(a.time)

    app.run()
