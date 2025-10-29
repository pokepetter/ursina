from typing import Literal

from ursina import curve
from ursina.audio import Audio
from ursina.string_utilities import print_warning
from ursina.ursinastuff import after

tracks = dict()
current_music_track = ''
current_ambiance_track = ''
prev_music_track = ''
prev_ambiance_track = ''


def _load_audio(track_name, audio_group='music'):
    audio_instance = Audio(track_name, loop=True, autoplay=False, group=audio_group, ignore_paused=True)
    if not audio_instance.clip:
        print_warning('track not found:', track_name)
        return None
    tracks[track_name] = audio_instance
    return audio_instance


def play(track_name, fade_out_duration=2, start=0, track_group:Literal['music','ambiance']='music'):
    global current_music_track, current_ambiance_track, prev_music_track, prev_ambiance_track

    if track_group == 'music':
        if track_name == current_music_track:
            return

        prev_music_track = current_music_track
        current_music_track = track_name
        # print(f'change music track: {prev_music_track} --> {current_music_track}')

    elif track_group == 'ambiance':
        if track_name == current_ambiance_track:
            return

        prev_ambiance_track = current_ambiance_track
        current_ambiance_track = track_name
        # print(f'change ambiance track: {prev_ambiance_track} --> {current_ambiance_track}')

    else:
        print_warning(f'Invalid audio group: {track_group}')
        return


    if track_name and track_name not in tracks:
        audio_group = track_group
        if track_group == 'ambiance':
            audio_group = 'ambient'
        audio = _load_audio(track_name, audio_group)
        if audio is None:
            print_warning('audio not found:', track_name)

    prev_track = prev_music_track if track_group == 'music' else prev_ambiance_track
    current_track = current_music_track if track_group == 'music' else current_ambiance_track

    if not prev_track:  # if no music/ambiance playing, start immediately
        tracks[current_track].play(start)
        tracks[current_track].volume = 1
        return

    # fade out prev track and play new one after
    if prev_track:
        tracks[prev_track].fade_out(duration=fade_out_duration, curve=curve.linear, destroy_on_ended=False, ignore_paused=True)

    if not current_track:
        return

    @after(fade_out_duration, ignore_paused=True)
    def _():
        tracks[current_track].play(start=start)
        tracks[current_track].fade_in(duration=fade_out_duration, curve=curve.linear, ignore_paused=True)


def play_ambiance(track_name, fade_out_duration=2, start=0):
    play(track_name, fade_out_duration, start, track_group='ambiance')


if __name__ == '__main__':
    from ursina import *
    from ursina import music_system

    app = Ursina()

    # music_system.play('noise', track_group='music')
    # music_system.play('forest', track_group='ambiance')

    # def input(key):
    #     if key == 'space':
    #         if music_system.current_music_track == 'noise':
    #             music_system.play('square', track_group='music')
    #         else:
    #             music_system.play('noise', track_group='music')

    #     if key == 'a':
    #         if music_system.current_ambiance_track == 'forest':
    #             music_system.play('rain', track_group='ambiance')
    #         else:
    #             music_system.play('forest', track_group='ambiance')
    music_changer = ButtonGroup(('', 'crestlands_part', 'dunes_part'), label='music', )
    def on_music_selected():
        music_system.play(music_changer.value if music_changer.value != 'None' else None)
    music_changer.on_value_changed = on_music_selected

    ambiance_changer = ButtonGroup(('', 'noise', 'square'), label='ambiance', y=-.1)
    def on_ambiance_selected():
        music_system.play_ambiance(ambiance_changer.value if ambiance_changer.value != 'None' else None)
    ambiance_changer.on_value_changed = on_ambiance_selected

    t = Text('SPACE: Toggle music\nA: Toggle ambiance', origin=(0, 0), y=-.4)
    def update():
        t.text = f'''\
            current_music_track:    {music_system.current_music_track},
            prev_music_track: {music_system.prev_music_track},

            current_ambiance_track: {music_system.current_ambiance_track},
            prev_ambiance_track: {music_system.prev_ambiance_track},
            '''

    app.run()
