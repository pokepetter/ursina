from ursina import *

class Audio():
    def __init__(self, sound_file_name='', autoplay=True, **kwargs):
        printvar(sound_file_name)
        self.clip = None
        if sound_file_name != '':
            self.clip = sound_file_name

        self.attack = 0
        self.falloff = 0 # start fading out n seconds before the end
        self.loop = False
        # self.loops = 3
        self.volume = 1
        self.pitch = 1
        self.balance = 0
        self.autoplay = True

        # self.volume_variation = 0
        # self.pitch_variation = 0

        for key, value in kwargs.items():
            setattr(self, key, value)

        if autoplay:
            self.play()

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'clip':
            if isinstance(value, str):
                self.name = value
                self.clip = loader.loadSfx(value + '.wav')

        if self.clip:
            if name == 'volume':
                self.clip.setVolume(value)

            if name == 'pitch':
                self.clip.setPlayRate(value)

            if name == 'loop':
                self.clip.setLoop(value)

            if name == 'loops':
                self.clip.setLoopCount(value)

    @property
    def length(self):
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

    def statu(self):
        print(self.status)

    def play(self, start=0):
        if self.clip:
            # print('play from:', start)
            self.time = start
            self.clip.play()

    def pause(self):
        if self.clip:
            # self.paused_volume = self.volume
            self.paused_pitch = self.pitch
            # self.paused_balance = self.balance
            self.temp_time = self.time
            self.pitch = 0
            self.stop(destroy=False)

    def resume(self):
        if self.clip and hasattr(self, 'temp_time'):
            # self.clip = self.name
            # self.volume = self.paused_volume
            self.pitch = self.paused_pitch
            # self.balance = self.paused_balance
            # self.play(self.temp_time)

    def stop(self, destroy=True):
        if self.clip:
            self.clip.stop()
            # if destroy:
            #     destroy(self)


if __name__ == '__main__':
    app = Ursina()

    a = Audio('night_sky', pitch=.5, i = 0)
    DebugMenu(a)
    app.run()
