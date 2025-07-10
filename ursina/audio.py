from ursina import application  # noqa: I001
from ursina.entity import Entity
from ursina import curve
from ursina.ursinastuff import invoke
from ursina.destroy import destroy as _destroy
from ursina.string_utilities import print_warning
from ursina.scripts.property_generator import generate_properties_for_class
from pathlib import Path

from panda3d.core import Filename

from ursina.ursinastuff import DotDict
audio_groups = DotDict(
    music =     DotDict(volume_multiplier=1),
    ambient =   DotDict(volume_multiplier=1),
    sfx =       DotDict(volume_multiplier=1),
    dialogue =  DotDict(volume_multiplier=1),
)

audio_clip_cache = dict()

@generate_properties_for_class()
class Audio(Entity):

    volume_multiplier = .5  # master volume

    def __init__(self, sound_file_name='', volume=1, pitch=1, balance=0, loop=False, loops=1, autoplay=True, auto_destroy=False, group='sfx', **kwargs):
        super().__init__(**kwargs)
        # printvar(sound_file_name)
        self.clip = sound_file_name
        self.group = group
        if not self.clip:
            print_warning('missing audio clip:', sound_file_name)
            return

        self.volume = volume
        self.pitch = pitch
        self.balance = balance
        self.loop = loop
        if not loop:
            self.loops = loops
        self.autoplay = autoplay
        self.auto_destroy = auto_destroy


        if self.autoplay:
            self.play()

        if self.auto_destroy:
            invoke(self.stop, destroy=True, delay=self.length)


    def volume_setter(self, value):
        if not self._clip:  return
        self._volume = value
        group_volume_multiplier = audio_groups[self.group].volume_multiplier if self.group else 1
        self._clip.setVolume(value * Audio.volume_multiplier * group_volume_multiplier)

    def pitch_setter(self, value):
        if not self._clip:  return
        self._pitch = value
        self._clip.setPlayRate(value)

    def loop_setter(self, value):
        if not self._clip:  return
        self._loop = value
        self._clip.setLoop(value)

    def loops_setter(self, value):
        if not self._clip:  return
        self._loops = value
        self._clip.setLoopCount(value)


    def clip_setter(self, value):
        # if value in audio_clip_cache:
        #     self._clip = copy(audio_clip_cache[value])
        #     return

        if isinstance(value, Path):
            self._clip = loader.loadSfx(Filename.fromOsSpecific(str(value.resolve())))  # type: ignore
            return

        if isinstance(value, str):
            self.name = value

            if '.' in value:
                file_types = ('',)
            else:
                file_types = ('.ogg', '.wav', '.mp3')

            for folder in (application.asset_folder, application.internal_audio_folder):
                for suffix in file_types:
                    for f in folder.glob(f'**/{value}{suffix}'):
                        self.path = str(f.resolve())
                        self._clip = loader.loadSfx(Filename.fromOsSpecific(self.path))  # type: ignore
                        audio_clip_cache[value] = self._clip
                        # print('...loaded audio clip:', p, self._clip)
                        return

            self._clip = None
            print('no audio found with name:', value, 'supported formats: .ogg, .wav')
            return

        self._clip = value


    def length_getter(self):       # get the duration of the audio clip.
        return self.clip.length() if self.clip else 0

    def status_getter(self):
        if self.clip:
            return self.clip.status()

    def ready_getter(self):
        return 1 if self.clip and self.status > 0 else 0

    def playing_getter(self):
        return 1 if self.clip and self.status == 2 else 0

    def time_getter(self):
        return self.clip.get_time()
    def time_setter(self, value):
        self.clip.set_time(value)


    def balance_setter(self, value):    # pan the audio. should be a value between -.5 and .5. default: 0
        self._balance = value
        self.clip.setBalance(value*2)


    def play(self, start=0):
        if application.paused and not self.ignore_paused:
            return

        if self.clip:
            # print('play from:', start, self.clip)
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

    def fade(self, value, duration=.5, delay=0, curve=curve.in_expo, resolution=None, interrupt=True, ignore_paused=True):
        self.animate('volume', value=value, duration=duration, delay=delay, curve=curve, resolution=resolution, interrupt=interrupt, ignore_paused=ignore_paused)

    def fade_in(self, value=1, duration=.5, delay=0, curve=curve.in_expo, resolution=None, interrupt='finish', destroy_on_ended=False, ignore_paused=True):
        if duration+delay <= 0:
            self.volume = value
        else:
            self.animate('volume', value, duration=duration, delay=delay, curve=curve, resolution=resolution, interrupt=interrupt, ignore_paused=ignore_paused)
        if destroy_on_ended:
            _destroy(self, delay=delay+duration + .01)

    def fade_out(self, value=0, duration=.5, delay=0, curve=curve.in_expo, resolution=None, interrupt='finish', destroy_on_ended=True, ignore_paused=True):

        if duration+delay <= 0:
            self.volume = value
        else:
            self.animate('volume', value, duration=duration, delay=delay, curve=curve, resolution=resolution, interrupt=interrupt, ignore_paused=ignore_paused)
        if destroy_on_ended:
            _destroy(self, delay=delay+duration + .05)


if __name__ == '__main__':
    import random

    from ursina import Ursina

    app = Ursina()
    a = Audio('sine', loop=True, autoplay=True)

    a.volume = .5
    print('---', a.volume)
    # a = Audio('life_is_currency_wav', pitch=1)
    def input(key):
        if key == 'space':
            a = Audio('sine', pitch=random.uniform(.5,1), loop=True)
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
