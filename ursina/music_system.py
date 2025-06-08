from ursina.audio import Audio
from ursina.ursinastuff import invoke
from ursina import curve
from ursina.string_utilities import print_warning
from ursina.ursinastuff import after


tracks = dict()
current_track = ''

def _load_audio(track_name):
    audio_instance = Audio(track_name, loop=True, autoplay=False, group='music', ignore_paused=True)
    if not audio_instance.clip:
        print_warning('music track not found:', track_name)
        return
    tracks[track_name] = audio_instance


def play(track_name, fade_out_duration=2, start=0):
    global current_track

    if track_name == current_track:
        return

    if not track_name and current_track:
        tracks[current_track].fade_out(fade_out_duration)
        current_track = None
        return

    if track_name not in tracks:
        _load_audio(track_name)

    if not current_track:   # if no music playing, start immediately
        tracks[track_name].play(start)
        current_track = track_name
        return

    # fade out current track and play new one after
    print('music_system: fade out:', current_track)
    tracks[current_track].fade_out(duration=fade_out_duration, curve=curve.linear, destroy_on_ended=False, ignore_paused=True)
    print('music_system: fade in:', track_name)
    @after(fade_out_duration, ignore_paused=True)
    def _():
        tracks[track_name].play(start=start)
        tracks[track_name].fade_in(duration=fade_out_duration)
    # invoke(tracks[track_name].play, start=start, delay=fade_out_duration, ignore_paused=True)
    current_track = track_name


track_before_override = ''
override_timestamp = 0

def temporarily_override(track_name):
    global override_timestamp, track_before_override
    if track_name == current_track:
        print_warning('trying to override track to same as current:', track_name)
        return

    print('temporarily_override:', track_before_override, '-->', track_name)
    track_before_override = current_track
    if current_track:
        override_timestamp = tracks[current_track].time

    play(track_name)

def stop_override():
    play(track_before_override, start=override_timestamp)
    print('return to:', track_before_override, 'and start from:', override_timestamp)


if __name__ == '__main__':
    from ursina import *
    from ursina import music_system

    app = Ursina()

    music_system.play('noise')

    def input(key):
        if key == 'space':
            if music_system.current_track == 'noise':
                music_system.play('square')
            else:
                music_system.play('noise')

        if key == 'o':
            music_system.temporarily_override('square')
        elif key == 's':
            music_system.stop_override()

    Text('O: Override music\nS: Stop override', origin=(0,0), y=-.4)
    app.run()
