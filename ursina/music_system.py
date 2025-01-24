from ursina.audio import Audio
from ursina.ursinastuff import invoke
from ursina import curve
from ursina.string_utilities import print_warning


tracks = dict()
current_track:str = None

def play(track_name, fade_out_duration=2):
    global current_track

    if track_name == current_track:
        return

    if track_name is None and current_track:
        tracks[current_track].fade_out(fade_out_duration)
        current_track = None
        return

    if track_name not in tracks:
        audio_instance = Audio(track_name, loop=True, autoplay=False, group='music')
        if not audio_instance.clip:
            print_warning('music track not found:', track_name)
            return
        tracks[track_name] = audio_instance

    if current_track is None: # if no music playing, start immediately
        tracks[track_name].play()
        current_track = track_name
        return

    # fade out current track and play new one after
    print('music_system: fade out:', current_track)
    tracks[current_track].fade_out(duration=fade_out_duration, curve=curve.linear, destroy_on_ended=False, ignore_paused=True)
    tracks.pop(current_track, None)
    print('music_system: fade in:', track_name)
    invoke(tracks[track_name].play, delay=fade_out_duration, ignore_paused=True)
    current_track = track_name


if __name__ == '__main__':
    from ursina import *
    # from ursina import music_system

    app = Ursina()

    music_system.play('noise')

    def input(key):
        if key == 'space':
            if music_system.current_track == 'noise':
                music_system.play('square')
            else:
                music_system.play('noise')


    app.run()
