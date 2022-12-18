import ursina


class Menu(ursina.Entity):
    '''
    Main menu class. Allows you to turns on/off music and sound.
    '''

    def __init__(self) -> None:
        ursina.camera.orthographic = True
        ursina.camera.fov = 1
        ursina.window.fullscreen = True
        ursina.window.fps_counter.enabled = False
        super().__init__(
            model='quad',
            scale=(ursina.window.aspect_ratio, 1),
            texture=r'assets/images/menu.png'
        )
        self.build_buttons()
        self.is_music_on = True
        self.is_sound_on = True

    def build_buttons(self) -> None:
        '''Creates control buttons'''
        self.play_button = ursina.Button(
            icon=r'assets/images/play_button.png',
            scale=(0.5, 0.1),
            highlight_scale=1.1,
            y=0.1,
            color=ursina.color.rgba(0, 0, 0, 0)
        )

        self.music_button = ursina.Button(
            icon=r'assets/images/music_button.png',
            scale=(0.1, 0.1),
            highlight_scale=1.1,
            position=(-0.2, -0.2),
            color=ursina.color.rgba(0, 0, 0, 0)
        )
        self.music_button.on_click = self.click_on_music_button

        self.sound_button = ursina.Button(
            icon=r'assets/images/sound_button.png',
            scale=(0.1, 0.1),
            highlight_scale=1.1,
            position=(-0.05, -0.2),
            color=ursina.color.rgba(0, 0, 0, 0)
        )
        self.sound_button.on_click = self.click_on_sound_button

    def click_on_music_button(self) -> None:
        '''Turns on/off music. Changes the button image'''
        if self.is_music_on:
            self.is_music_on = False
            self.music_button.icon = r'assets/images/music_button_off.png'
        else:
            self.is_music_on = True
            self.music_button.icon = r'assets/images/music_button.png'

    def click_on_sound_button(self) -> None:
        '''Turns on/off sound. Changes the button image'''
        if self.is_sound_on:
            self.is_sound_on = False
            self.sound_button.icon = r'assets/images/sound_button_off.png'
        else:
            self.is_sound_on = True
            self.sound_button.icon = r'assets/images/sound_button.png'

    def destroy(self) -> None:
        '''Destroys self'''
        ursina.destroy(self.play_button)
        ursina.destroy(self.music_button)
        ursina.destroy(self.sound_button)
        ursina.destroy(self)
