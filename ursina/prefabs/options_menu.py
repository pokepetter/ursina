from ursina import Animator, Audio, Button, Entity, Slider, Text, audio, camera, color, hsv, scene
from ursina.prefabs.button_group import ButtonGroup


class MenuButton(Button):
    def __init__(self, text='', **kwargs):
        super().__init__(text, scale=(.25, .075), highlight_color=color.azure, **kwargs)
        for key, value in kwargs.items():
            setattr(self, key ,value)

# button_size = (.25, .075)
button_spacing = .05

class OptionsMenu(Entity):
    default_values = dict(parent=camera.ui)
    def __init__(self, **kwargs):
        super().__init__(**(__class__.default_values | kwargs))

        self.accessibility_menu = Entity(parent=self)
        self.accessibility_menu.preview_text = Text(parent=self.accessibility_menu, x=.275, y=.25, text='Preview text', origin=(-.5,0))
        for t in [e for e in scene.entities if isinstance(e, Text)]:
            t.original_scale = t.scale

        text_scale_slider = Slider(0, 2, default=1, step=.1, dynamic=True, text='Text Size', parent=self.accessibility_menu, x=-.25)
        def set_text_scale():
            for t in [e for e in scene.entities if isinstance(e, Text) and hasattr(e, 'original_scale')]:
                t.scale = t.original_scale * text_scale_slider.value
        text_scale_slider.on_value_changed = set_text_scale

        for i, e in enumerate(self.accessibility_menu.children):
            e.y = .3 + (-i * button_spacing)


        self.audio_settings_menu = Entity(parent=self)
        def update_volume_for_currently_playing():
            for e in scene.entities:
                if isinstance(e, Audio):
                    e.volume = e.volume

        volume_slider = Slider(0, 1, default=Audio.volume_multiplier, step=.1, text='Master Volume', parent=self.audio_settings_menu, x=-.25, dynamic=True)
        def set_volume(slider=volume_slider):
            Audio.volume_multiplier = slider.value
            update_volume_for_currently_playing()
        volume_slider.on_value_changed = set_volume

        for name, audio_group in audio.audio_groups.items():
            volume_slider = Slider(0, 1, default=audio_group.volume_multiplier, step=.1, text=f'{name.title()} Volume', parent=self.audio_settings_menu, x=-.25, dynamic=True)
            def set_volume(name=name, slider=volume_slider):
                audio.audio_groups[name].volume_multiplier = slider.value
                update_volume_for_currently_playing()
            volume_slider.on_value_changed = set_volume

        for i, e in enumerate(self.audio_settings_menu.children):
            e.y = .3 + (-i * button_spacing)

        self.graphics_menu = Entity(parent=self)
        window_mode_setting = ButtonGroup(('Borderless Fullscreen', 'Windowed'), y=.3, origin=(0,.5), parent=self.graphics_menu, label='Window Mode')
        def _set_window_mode():
            if window_mode_setting.value == window_mode_setting.options[0]:
                window.borderless = True
                window.fullscreen = True
            elif window_mode_setting.value == window_mode_setting.options[1]:
                window.borderless = False
                # window.size = window.windowed_size
        window_mode_setting.on_value_changed = _set_window_mode

        window_index_setting = ButtonGroup([f'{i: ^10}' for i in range(len(window.monitors))], y=.3, origin=(0,.5), parent=self.graphics_menu, label='Monitor')

        for i, e in enumerate((window_mode_setting, window_index_setting)):
            e.y = .3 + (-i * button_spacing*3)


        self.language_menu = Entity(parent=self)
        ButtonGroup(('English', 'Mandarin Chinese (官话)', 'Spanish (español)', 'Japanese (日本語 )', 'German (Deutsch)', 'Norwegian (bokmål)'), y=.3, origin=(0,.5), parent=self.language_menu, max_x=1)

        self.controls_menu = Entity(parent=self)

        self.state_handler = Animator({
            'controls' :        self.controls_menu,
            'graphics' :        self.graphics_menu,
            'audio' :           self.audio_settings_menu,
            'accessibility' :   self.accessibility_menu,
            'language' :        self.language_menu,
            }
        )

        # self.side_menu = ButtonList({key.title(): Func(setattr, self.state_handler, 'state', key) for key, value in self.state_handler.animations.items()},
        #     parent=self, position=window.left, origin=(-.5,0),)
        # self.side_menu = Entity(parent=self, position=window.left)
        # for key, value in self.state_handler.animations.items():
        #     MenuButton(parent=self.side_menu, text=key.title(), on_click=Func(setattr, self.state_handler, 'state', key), origin_x=-.5)
        # grid_layout(self.side_menu.children, max_x=1, spacing=(0,.01), origin=(-.5,0))
        tabs = ButtonGroup([f'{e.title(): ^24}' for e in self.state_handler.animations.keys()], origin=(0,0), y=.45)
        def on_tab_changed():
            self.state_handler.state = tabs.value.strip().lower()
        tabs.on_value_changed = on_tab_changed
        # # options_back = MenuButton(parent=options_menu, text='Back', x=-.25, origin_x=-.5, on_click=Func(setattr, state_handler, 'state', 'main_menu'))



if __name__ == '__main__':
    from ursina import Ursina, window, Button
    app = Ursina()
    # Text.default_font = 'VeraMono.ttf'
    window.color = hsv(0, 0, 10/255)
    Button.default_color = color._24
    Button.default_highlight_color = color._32
    # ButtonGroup.default_selected_color = color.hex('#85a9f7')
    # ButtonGroup.default_selected_color = color.hex('#ff5eef')
    # ButtonGroup.default_selected_color = color.hex('#85a9f7')
    # color.text_color = hsv(240, 1, .8)
    # color.text_color = hsv(60, 0, 10/255)
    # Button.default_color
    options_menu = OptionsMenu()
    # window.color = color._16
    background = Entity(parent=camera.ui, model='quad', texture='shore', scale=(camera.aspect_ratio,1), color=color.dark_gray, z=1, world_y=0)
    # Audio('chillstep_1.ogg', loop=True, group='music')
    app.run()
