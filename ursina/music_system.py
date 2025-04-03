"""
ursina/music_system.py

This module provides a simple music system for the Ursina engine.
It allows for playing, fading out, and switching between different music tracks.

Dependencies:
- ursina.audio.Audio
- ursina.ursinastuff.invoke
- ursina.curve
- ursina.string_utilities.print_warning
"""

from ursina.audio import Audio
from ursina.ursinastuff import invoke
from ursina import curve
from ursina.string_utilities import print_warning

# Dictionary to store the audio tracks
tracks = dict()
# Variable to keep track of the current playing track
current_track: str = None

def play(track_name, fade_out_duration=2):
    """
    Play a music track with optional fade out duration for the current track.

    Args:
        track_name (str): The name of the track to play.
        fade_out_duration (float, optional): The duration to fade out the current track. Defaults to 2.

    Returns:
        None
    """
    global current_track

    # If the track is already playing, do nothing
    if track_name == current_track:
        return

    # If no track name is provided and a track is currently playing, fade it out
    if track_name is None and current_track:
        tracks[current_track].fade_out(fade_out_duration)
        current_track = None
        return

    # If the track is not in the dictionary, create a new Audio instance and add it to the dictionary
    if track_name not in tracks:
        audio_instance = Audio(track_name, loop=True, autoplay=False, group='music')
        if not audio_instance.clip:
            print_warning('music track not found:', track_name)
            return
        tracks[track_name] = audio_instance

    # If no music is currently playing, start the new track immediately
    if current_track is None:
        tracks[track_name].play()
        current_track = track_name
        return

    # Fade out the current track and play the new one after the fade out duration
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
