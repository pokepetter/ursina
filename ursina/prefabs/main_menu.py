from ursina import *
from ursina.ursinastuff import DotDict

# class button_classButton):
#     def __init__(self, text='', **kwargs):
#         super().__init__(text=text, scale=(.25, .075), highlight_color=color.azure, **kwargs)
#         for k, v in kwargs.items():
#             setattr(self, k, v)


class MainMenu(Entity):
    def __init__(self, button_class=Button, button_size=Vec2(.25,.075), **kwargs):
        super().__init__(parent=camera.ui)
        self.button_size= button_size
        for key, value in kwargs.items():
            setattr(self, key, value)

        button_spacing = .075 * 1.25

        self.menu_parent = Entity(parent=self, y=0)
        self.main_menu = Entity(parent=self.menu_parent, y=.15)
        self.load_menu = Entity(parent=self.menu_parent)
        # self.options_menu = Entity(parent=self.menu_parent)
        from ursina.prefabs.options_menu import OptionsMenu
        self.options_menu = OptionsMenu(parent=camera.ui, enabled=False)

        self.state_handler = Animator({
            'main_menu': self.main_menu,
            'load_menu': self.load_menu,
            'options_menu': self.options_menu
        })

        self.options_menu.on_close = Func(setattr, self.state_handler, 'state', 'main_menu')   # so we can get back from the options menu

        self.main_menu.buttons = DotDict(
            new = button_class(text='New Game', scale=button_size, on_click=Func(print_on_screen, 'Assign MainMenu().main_menu.buttons.new.on_click', origin=(0,0), position=(0,.1,-1), color=color.red)),
            load = button_class(text='Load', scale=button_size, on_click=Func(setattr, self.state_handler, 'state', 'load_menu')),
            options = button_class(text='Options', scale=button_size, on_click=Func(setattr, self.state_handler, 'state', 'options_menu')),
            quit = button_class(text='Quit', scale=button_size, on_click=application.quit),
        )

        for i, (name, button) in enumerate(self.main_menu.buttons.items()):
            button.parent = self.main_menu
            button.y = (-i - 2) * button_spacing

        self.main_menu.buttons.load.buttons = []
        for i in range(3):
            b = button_class(parent=self.load_menu, scale=button_size, text=f'Slot {i}', y=-i * button_spacing)
            self.main_menu.buttons.load.buttons.append(b)

        button_class(parent=self.load_menu, scale=button_size, text='Back', y=-5 * button_spacing, on_click=Func(setattr, self.state_handler, 'state', 'main_menu'))


        # text_scale_slider = Slider(0, 2, default=1, step=.1, dynamic=True, text='Text Size:', parent=self.options_menu, x=-.25)
        # text_preview = Text(parent=self.options_menu, position=text_scale_slider.position+Vec2(.55,0), text='Preview text', origin=(-.5, 0))
        # text_preview.original_scale = text_preview.scale

        # master_volume_slider = Slider(0, 1, default=Audio.volume_multiplier, step=.1, text='Master Volume:', parent=self.options_menu, x=-.25)
        # def set_text_scale():
        #     for e in scene.entities:
        #         if isinstance(e, Text) and hasattr(e, 'original_scale'):
        #             e.scale = e.original_scale * text_scale_slider.value

        # text_scale_slider.on_value_changed = set_text_scale


        # volume_sliders = [master_volume_slider, ]
        # for name, data in audio.audio_groups.items():
        #     volume_slider = Slider(0, 1, default=data.volume_multiplier, step=.1, text=f'{name.title()} Volume:', parent=self.options_menu, x=-.25)
        #     volume_sliders.append(volume_slider)
        #     def set_volume(group=name):
        #         for e in scene.entities:
        #             if isinstance(e, Audio) and e.group == group:
        #                 e.volume = e.volume

        #     volume_slider.on_value_changed = set_volume
        # options_bg = Panel(loose_parent=self.options_menu, scale=Vec2(1,.75), z=.1)

        # settings_file_path = Path('ursina_general_settings.txt')
        # def save_settings():
        #     with settings_file_path.open('w') as f:
        #         f.write('# settings file for ursina main menu')

        # options_back = button_class(parent=self.options_menu, scale=button_size, text='Back', x=-.125-.025, y=-.4, scale_x=.125, origin_x=-.5, on_click=Func(setattr, self.state_handler, 'state', 'main_menu'))
        # options_save = button_class(parent=self.options_menu, scale=button_size, text='Save', x=0, y=options_back.y, origin_x=-.5, on_click=Func(setattr, self.state_handler, 'state', 'main_menu'))

        # for i, e in enumerate((text_scale_slider, *volume_sliders)):
        #     e.y = -i * button_spacing * .5

        target_alpha = self.main_menu.buttons.new.alpha
        for menu in (self.main_menu, self.load_menu, self.options_menu):
            def animate_in(menu=menu):
                for i, e in enumerate(menu.children):
                    e.original_x = e.x
                    e.x += .1
                    e.animate_x(e.original_x, delay=i * .05, duration=.1, curve=curve.out_quad)
                    e.alpha = 0
                    e.animate('alpha', target_alpha, delay=i * .05, duration=.1, curve=curve.out_quad)
                    if hasattr(e, 'text_entity'):
                        e.text_entity.alpha = 0
                        e.text_entity.animate('alpha', 1, delay=i * .05, duration=.1)
            menu.on_enable = animate_in

        self.state_handler.state = 'main_menu'


if __name__ == '__main__':
    app = Ursina()
    MainMenu()
    app.run()
