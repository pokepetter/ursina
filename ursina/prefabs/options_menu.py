from ursina import Animator, Audio, Button, Entity, Slider, Text, audio, camera, color, hsv, scene, Vec2, window, Quad, Func
from ursina.prefabs.button_group import ButtonGroup
from ursina.prefabs.key_picker import KeyPicker



class MenuButton(Button):
    def __init__(self, text='', **kwargs):
        super().__init__(text, scale=(.25, .075), highlight_color=color.azure, **kwargs)
        for key, value in kwargs.items():
            setattr(self, key ,value)

# button_size = (.25, .075)
button_spacing = .05

class OptionsMenu(Entity):
    default_values = dict(parent=camera.ui)
    def __init__(self, z=-100, on_close:callable=Func(print, 'close'), **kwargs):
        super().__init__(z=z, **(__class__.default_values | kwargs))
        self.on_close = on_close
        self.bg = Entity(parent=self, z=.01, scale=Vec2(1.1,.875), color=hsv(0,0,.1))
        self.bg.model = Quad(aspect=self.bg.scale.x/self.bg.scale.y, radius=.01)
        self.accessibility_menu = Entity(parent=self)

        text_scale_slider = Slider(0, 2, default=1, step=.1, dynamic=True, text='Text Size', parent=self.accessibility_menu, x=-.25)
        self.accessibility_menu.preview_text = Text(parent=text_scale_slider, position=Vec2(.55,0), text='Preview text', origin=(-.5,0))
        for t in [e for e in scene.entities if isinstance(e, Text)]:
            t.original_scale = t.scale
        def set_text_scale():
            for t in [e for e in scene.entities if isinstance(e, Text) and hasattr(e, 'original_scale')]:
                t.scale = t.original_scale * text_scale_slider.value
        text_scale_slider.on_value_changed = set_text_scale

        from ursina.prefabs.checkbox import Checkbox
        Text(parent=self.accessibility_menu, text='disable_screenshake', x=-.5)
        disable_screenshake_checkbox = Checkbox(parent=self.accessibility_menu, label='disable_screenshake:', color=color.black, scale=.035)

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

        # from ursina.prefabs.dropdown_menu import DropdownMenu, DropdownMenuButton
        # resolution_setting = DropdownMenu()

        for i, e in enumerate((window_mode_setting, window_index_setting)):
            e.y = .3 + (-i * button_spacing*3)


        self.language_menu = Entity(parent=self)
        ButtonGroup((
            'English',
            # 'Mandarin Chinese (官话)',
            # 'Spanish (español)',
            # 'Japanese (日本語 )',
            # 'German (Deutsch)',
            'Norwegian (bokmål)'
            ), y=.3, origin=(0,.5), parent=self.language_menu, max_x=1)

        self.controls_menu = Entity(parent=self)
        from ursina import input_handler, grid_layout
        # rebind_fields = []
        rebinds = {}
        for input_key, emitted_keys in input_handler.rebinds.items():
            for e in emitted_keys:
                if e not in input_handler.Keys and len(e.split(' ',1)[0]) > 1 and not e.endswith(' up') and not e.endswith(' hold') and e != 'space':
                    rebinds[e] = input_key

        longest_word = sorted([(len(w), w) for w in rebinds.keys()], reverse=True)[0][1]
        max_width = Text.get_width(longest_word+'    ', Text.default_monospace_font)
        # print('max_width:', max_width, longest_word)

        # [0][1]
        self.rebind_fields = dict()
        for i, (key, value) in enumerate(rebinds.items()):
            text = Text(parent=self.controls_menu, font=Text.default_monospace_font, text=f'{key}:', text_origin=(-.5,0), scale=.75, origin=Vec2(-.5,0), position=Vec2(-.5,.35+(-i*.04)))
            field = Button(parent=self.controls_menu, text=f'{value}', scale=Vec2(.25,.035), origin=(-.5,0), text_origin=(-.5,0), text_size=.75, x=text.x+(max_width*text.scale.x), y=text.y, color=color.hsv(0,0,.05,1))
            field.text_entity.font = Text.default_monospace_font
            def on_picked_key(new_key):
                print('picked key:', self.key_picker.action, self.key_picker.old_key, new_key)
                input_handler.unbind(self.key_picker.old_key)
                input_handler.bind(self.key_picker.action, new_key)

            def open_key_picker(field=field, action=key):
                self.key_picker.target_field = field
                self.key_picker.enabled = True
                self.key_picker.action = action     # action is the name used for the in-game action, like 'attack', 'back', etc.
                self.key_picker.old_key = field.text
                self.key_picker.on_submit = on_picked_key
            field.on_click = open_key_picker
            self.rebind_fields[key] = field

            # rebind_fields.append(text)
        self.key_picker = KeyPicker(parent=self, enabled=False, z=-1)

        def save_keybinds(close_options_menu=True):
            for name, field in self.rebind_fields.items():
                print('---:', f'input_handler.rebind(\'{field.text}\', \'{name}\')')
            if close_options_menu:
                self.enabled = False
                if self.on_close:
                    self.on_close()

        save_button = Button(parent=self.controls_menu, scale=(.15,.05), color=color.azure, position=(0,-.39), text='Save\n(not yet implemented)', on_click=save_keybinds)
        back_button = Button(parent=self.controls_menu, scale=(.075,.05), color=color.hsv(0,0,.05,1), position=(-save_button.scale_x,-.39,), text='Back', on_click=save_keybinds)
        # print('rebind_fields:', rebind_fields)
        # if rebind_fields:
        #     grid_layout(rebind_fields, max_x=1, offset=Vec2(-.5,.4), spacing=Vec2(.2,.005))

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
        tabs = ButtonGroup([f'{e.title(): ^24}' for e in self.state_handler.animations.keys()], parent=self, origin=(0,0), y=.45)
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

    # from ursina import NineSlice
    # NineSlice.outset = .4
    # Button.default_color = color.white
    # Button.default_model = NineSlice
    # Button.default_texture = 'nineslice_rainbow'
    # Button.default_radius = .5
    from ursina import input_handler
    input_handler.bind('right mouse down',          'blink')
    input_handler.bind('left mouse down',           'attack')
    input_handler.bind('left mouse up',             'attack up')
    input_handler.bind('space',                     'jump')
    input_handler.bind('r',                         'hookshot')
    input_handler.bind('e',                         'open spell menu')
    input_handler.bind('e up',                      'close spell menu')
    input_handler.bind('f',                         'loot')
    input_handler.bind('q',                         'open radial menu')
    input_handler.bind('q up',                      'close radial menu')

    options_menu = OptionsMenu()
    # window.color = color._16
    background = Entity(parent=camera.ui, model='quad', texture='shore', scale=(camera.aspect_ratio,1), color=color.dark_gray, z=1, world_y=0)
    # Audio('chillstep_1.ogg', loop=True, group='music')
    app.run()
