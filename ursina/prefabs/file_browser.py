from ursina import *
from ursina.scripts.property_generator import generate_properties_for_class

@generate_properties_for_class()
class FileButton(Button):
    def __init__(self, load_menu, path, **kwargs):
        self.load_menu = load_menu
        self.path = path
        super().__init__(model='quad', highlight_color=color.dark_gray, scale=(.875,.025), pressed_scale=1, ignore_paused=True, **kwargs)
        self.text_entity.scale *= .75
        self.original_color = self.color
        self.selected = False


    def on_click(self):
        if len([e for e in self.parent.children if e.selected]) >= self.load_menu.selection_limit and not self.selected:
            for e in self.parent.children:  # clear selection
                e.selected = False

        self.selected = not self.selected
        if self.selected:
            self.load_menu.address_bar.text_entity.text = '<light_gray>' + str(self.path.resolve())
        else:
            self.load_menu.address_bar.text_entity.text = '<light_gray>' + str(self.load_menu.path.resolve())


    def on_double_click(self):
        if self.path.is_dir():
            self.load_menu.path = self.path
        else:
            self.selected = True
            self.load_menu.open()


    def selected_setter(self, value):
        self._selected = value
        if value == True:
            self.color = color.azure
            self.highlight_color = color.azure.tint(.1)
        else:
            self.color = self.original_color
            self.highlight_color = color.dark_gray

        self.load_menu.open_button.color = color.azure if self.load_menu.selection else color.dark_gray



@generate_properties_for_class()
class FileBrowser(Entity):
    def __init__(self, file_button_class=FileButton, selection_limit=1, start_path=None, **kwargs):
        self.file_types = ['.*', ]
        if not start_path:
            start_path = Path('.').resolve()
        self.start_path = start_path
        self.file_button_class = file_button_class
        kwargs = dict(ignore_paused=True) | kwargs

        super().__init__(parent=camera.ui, y=.45, **kwargs)

        self.return_files = True
        self.return_folders = False
        self.selection_limit = selection_limit
        self.max_buttons = 24

        self.title_bar = Button(parent=self, scale=(.9,.035), text='<gray>Open', color=color.dark_gray, highlight_color=color.dark_gray)
        self.address_bar = Button(parent=self, scale=(.8,.035), text='//', text_origin=(-.5,0), y=-.05, highlight_color=color.black)
        self.address_bar.text_entity.scale *= .75
        self.address_bar.text_entity.x = -.5 + Text.get_width(' ')
        self.address_bar.text_entity.color = color.red

        self.folder_up_button = Button(parent=self, scale=(.035,.035), texture='arrow_down', rotation_z=180, position=(-.42,-.05,-1), color=color.white, highlight_color=color.azure, on_click=self.folder_up)
        self.button_parent = Entity(parent=self)
        self.back_panel = Entity(parent=self, model='quad', collider='box', origin_y=.5, scale=(.9,(self.max_buttons*.025)+.19), color=color._32, z=.1)
        self.bg = Button(parent=self, z=1, scale=(999,999), color=color.black66, highlight_color=color.black66, pressed_color=color.black66)

        self.cancel_button = Button(parent=self, scale=(.875*.24, .05), y=(-self.max_buttons*.025)-.15, origin_x=-.5, x=-.875/2, text='Cancel', on_click=self.close)
        self.open_button = Button(parent=self, scale=(.875*.74, .05), y=(-self.max_buttons*.025)-.15, origin_x=.5, x=.875/2, text='Open', color=color.dark_gray, on_click=self.open)

        self.cancel_button_2 = Button(parent=self.title_bar, model=Circle(), world_scale=self.title_bar.world_scale_y*.75, origin_x=.5, x=.495, z=-.1, text='<gray>x', on_click=self.close)
        self.cancel_button_2.text_entity.scale *= .75

        self.can_scroll_up_indicator = Entity(parent=self, model='quad', texture='arrow_down', rotation_z=180, scale=(.05,.05), y=-.0765, z=-.1, color=color.dark_gray, enabled=False, add_to_scene_entities=False)
        self.can_scroll_down_indicator = Entity(parent=self, model='quad', texture='arrow_down', scale=(.05,.05), y=(-self.max_buttons*.025)-.104, z=-.1, color=color.dark_gray, enabled=False, add_to_scene_entities=False)

        for key, value in kwargs.items():
            setattr(self, key ,value)



    def input(self, key):
        if key == 'scroll down':
            if self.scroll + self.max_buttons < len(self.button_parent.children)-1:
                self.scroll += 1

        if key == 'scroll up':
            if self.scroll > 0:
                self.scroll -= 1


    def scroll_setter(self, value):
        self._scroll = value

        for i, c in enumerate(self.button_parent.children):
            if i < value or i >= value + self.max_buttons:
                c.enabled = False
            else:
                c.enabled = True

        self.button_parent.y = value * .025
        self.can_scroll_up_indicator.enabled = value > 0
        self.can_scroll_down_indicator.enabled = value + self.max_buttons + 1 != len(self.button_parent.children)


    def path_setter(self, value):
        if not value:
            value = self.start_path

        self._path = value
        self.address_bar.text_entity.text = '<light_gray>' + str(value.resolve())

        files = [e for e in value.iterdir() if e.is_dir() or e.suffix in self.file_types or '.*' in self.file_types]
        files.sort(key=lambda x : x.is_file())  # directories first

        for i in range(len(self.button_parent.children) - len(files)):
            destroy(self.button_parent.children.pop())


        for i, f in enumerate(files):
            prefix = ' <light_gray>'
            # if f.is_dir():
            #     prefix = '<gray> <image:folder>   <light_gray>'
            # else:
            #     prefix = ' <light_gray> <image:file_icon>   <default>'
            if i < len(self.button_parent.children):
                # just update button name and path
                self.button_parent.children[i].text_entity.text = prefix + f.name
                self.button_parent.children[i].path = f

            else:
                # print('create new:', i)
                b = self.file_button_class(parent=self.button_parent, path=f, text_origin=(-.5,0), text=prefix+f.name, y=-i*.025 -.09, load_menu=self, add_to_scene_entities=False)

        self.scroll = 0


    def on_enable(self):
        # print('-------------', 'start path:', self.start_path)
        if not hasattr(self, 'path'):
            self.path = self.start_path
            self.scroll = 0
            return

        self.path = self.path if hasattr(self, 'path') else self.start_path
        self.button_parent.y = 0
        self.scroll = 0


    def close(self):
        self.enabled = False


    def folder_up(self):
        self.path = self.path.parent


    def open(self, path=None):
        if not self.selection:
            return

        if not self.return_folders and self.selection[0].is_dir():
            self.path = self.selection[0]
            return

        if hasattr(self, 'on_submit'):
            self.on_submit(self.selection)

        self.close()


    def selection_getter(self):
        return [c.path for c in self.button_parent.children if c.selected == True]




if __name__ == '__main__':
    app = Ursina()

    fb = FileBrowser(file_types=('.*'), enabled=False)

    def on_submit(paths):
        print('--------', paths)
        for p in paths:
            print('---', p)

    fb.on_submit = on_submit

    def input(key):
        if key == 'tab':
            fb.enabled = not fb.enabled


    app.run()
