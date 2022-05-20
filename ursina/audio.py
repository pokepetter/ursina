from ursina import *
from panda3d.core import Filename

# Set to avoid name-space conflicts in the Audio class.
_destroy = destroy


class Audio(Entity):

    volume_multiplier = .5  #

    def __init__(self, sound_file_name='', autoplay=True, auto_destroy=False, **kwargs):
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
    def clip(self, value):
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
                        self._clip = loader.loadSfx(p)
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
    def length(self):       # get the duration of the audio clip.
        return self.clip.length() if self.clip else 0

    @property
    def status(self):
        if self.clip:
            return self.clip.status()

    @property
    def ready(self):
        return 1 if self.clip and self.status > 0 else 0

    @property
    def playing(self):
        return 1 if self.clip and self.status == 2 else 0

    @property
    def time(self):
        return self.clip.get_time()

    @time.setter
    def time(self, value):
        self.clip.set_time(value)

    @property
    def balance(self):      # pan the audio. should be a value between -.5 and .5. default: 0
        return self._balance

    @balance.setter
    def balance(self, value):
        self._balance = value
        self.clip.setBalance(value*2)


    def play(self, start=0):
        if hasattr(self, 'clip') and self.clip:
            # print('play from:', start)
            self.time = start
            self.clip.play()
        else:
            print(self, 'has no audio clip')

    def pause(self):
        if self.clip:
            self.paused_volume = self.volume
            self.paused_pitch = self.pitch
            self.paused_balance = self.balance
            self.temp_time = self.time
            self.pitch = 0
            self.stop(destroy=False)

    def resume(self):
        if self.clip and hasattr(self, 'temp_time'):
            self.clip = self.name
            self.volume = self.paused_volume
            self.pitch = self.paused_pitch
            self.balance = self.paused_balance
            self.play(self.temp_time)

    def stop(self, destroy=True):
        if self.clip:
            self.clip.stop()
        if destroy:
            _destroy(self)

    def fade(self, value, duration=.5, delay=0, curve=curve.in_expo, resolution=None, interrupt=True):
        self.animate('volume', value, duration, delay, curve, resolution, interrupt)

    def fade_in(self, value=1, duration=.5, delay=0, curve=curve.in_expo, resolution=None, interrupt='finish',
                destroy_on_ended=False):
        if duration <= 0:
            self.volume = value
        else:
            self.animate('volume', value, duration=duration, delay=delay, curve=curve, resolution=resolution, interrupt=interrupt)
        if destroy_on_ended:
            _destroy(self, delay=duration + .01)

    def fade_out(self, value=0, duration=.5, delay=0, curve=curve.in_expo, resolution=None, interrupt='finish',
                 destroy_on_ended=True):
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
