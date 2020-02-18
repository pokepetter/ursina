from ursina import *


class FileButton(Button):
    def __init__(self, load_menu, **kwargs):
        super().__init__(
            model='quad',
            highlight_color = color.orange,
            scale = (.875,.025),
            pressed_scale = 1,
            selected = False,
            )
        self.load_menu = load_menu

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.text_entity.scale *= .75


    def on_click(self):
        if len(self.load_menu.selection) >= self.load_menu.selection_limit and not self.selected:
            for e in self.load_menu.selection:
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
            self.load_menu.open(self.path)


    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        if value == True:
            self.color = color.azure
            self.highlight_color = color.azure
        else:
            self.color = Button.color

        self.load_menu.open_button.color = color.azure if self.load_menu.selection else color.dark_gray



class FileBrowser(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, scale=(1,1), model='quad', color=color.clear, collider='box', y=.45)

        self.return_files = True
        self.return_directories = False
        self.selection_limit = 1
        self.max_buttons = 24

        self.title_bar = Button(parent=self, scale=(.9,.025), text='Open', color=color.dark_gray, collision=False, y=-.01)
        self.address_bar = Button(parent=self, scale=(.8,.035), text='//', text_origin=(-.5,0), y=-.05, highlight_color=color.black)
        self.address_bar.text_entity.scale *= .75
        self.address_bar.text_entity.x = -.5 + Text.get_width(' ')
        self.address_bar.text_entity.color = color.red

        self.folder_up_button = Button(parent=self, scale=(.035,.035), texture='arrow_down', rotation_z=180, position=(-.42,-.05), color=color.white, highlight_color=color.azure, on_click=self.folder_up)
        self.button_parent = Entity(parent=self)
        self.back_panel = Entity(parent=self, model='quad', collider='box', origin_y=.5, scale=(.9,(self.max_buttons*.025)+.19), color=color._32, z=.1)
        self.bg = Button(parent=self, z=1, scale=(999,999), color=color.black66, highlight_color=color.black66, pressed_color=color.black66)

        self.cancel_button = Button(parent=self, scale=(.875*.24, .05), y=(-self.max_buttons*.025)-.15, origin_x=-.5, x=-.875/2, text='Cancel', on_click=self.close)
        self.open_button = Button(parent=self, scale=(.875*.74, .05), y=(-self.max_buttons*.025)-.15, origin_x=.5, x=.875/2, text='Open', color=color.dark_gray, on_click=self.open)

        self.can_scroll_up_indicator = Entity(parent=self, model='quad', texture='arrow_down', rotation_z=180, scale=(.05,.05), y=-.0765, z=-.1, color=color.dark_gray, enabled=False, add_to_scene_entities=False)
        self.can_scroll_down_indicator = Entity(parent=self, model='quad', texture='arrow_down', scale=(.05,.05), y=(-self.max_buttons*.025)-.104, z=-.1, color=color.dark_gray, enabled=False, add_to_scene_entities=False)

        self.file_types = ['.*', ]
        self.start_path = Path('.').resolve()

        for key, value in kwargs.items():
            setattr(self, key ,value)

        if self.enabled:
            self.path = self.start_path     # this will populate the list
            self.scroll = 0


    def input(self, key):
        if key == 'scroll down':
            if self.scroll + self.max_buttons < len(self.button_parent.children)-1:
                self.scroll += 1

        if key == 'scroll up':
            if self.scroll > 0:
                self.scroll -= 1


    @property
    def scroll(self):
        return self._scroll

    @scroll.setter
    def scroll(self, value):
        self._scroll = value

        for i, c in enumerate(self.button_parent.children):
            if i < value or i > value + self.max_buttons:
                c.enabled = False
            else:
                c.enabled = True

        self.button_parent.y = value * .025
        self.can_scroll_up_indicator.enabled = value > 0
        self.can_scroll_down_indicator.enabled = value + self.max_buttons + 1 != len(self.button_parent.children)


    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        self.address_bar.text_entity.text = '<light_gray>' + str(value.resolve())


        files = [e for e in value.iterdir() if e.is_dir() or e.suffix in self.file_types or '.*' in self.file_types]
        files.sort(key=lambda x : x.is_file())  # directories first

        for i in range(len(self.button_parent.children) - len(files)):
            destroy(self.button_parent.children.pop())


        for i, f in enumerate(files):
            prefix = ' <light_gray>'
            if f.is_dir():
                prefix = '<gray> <image:folder>   <light_gray>'
            # else:
            #     prefix = ' <light_gray> <image:file_icon>   <default>'
            if i < len(self.button_parent.children):
                # just update button name and path
                self.button_parent.children[i].text_entity.text = prefix + f.name
                self.button_parent.children[i].path = f

            else:
                # print('create new:', i)
                b = FileButton(
                    parent = self.button_parent,
                    text = prefix + f.name,
                    text_origin = (-.5, 0),
                    y = -i*.025 -.09,
                    load_menu = self,
                    path = f,
                    add_to_scene_entities = False
                    )

        self.scroll = 0


    def on_enable(self):
        if not hasattr(self, 'path'):
            self.path = self.start_path
            invoke(setattr, self, 'scroll', 0, delay=.05)
            return

        self.scale = 1
        self.path = self.path
        self.button_parent.y = 0
        invoke(setattr, self, 'scroll', 0, delay=.1)


    def close(self):
        self.enabled = False


    def folder_up(self):
        self.path = self.path.parent


    def open(self):
        if len(self.selection) == 1 and self.selection[0].path.is_dir():
            self.path = self.selection[0].path
            return

        if hasattr(self, 'on_submit'):
            self.on_submit([e.path for e in self.selection])

        self.close()


    @property
    def selection(self):
        return [c for c in self.button_parent.children if c.selected == True]





if __name__ == '__main__':
    app = Ursina()

    fb = FileBrowser(file_types=('.*'), enabled=True)

    def on_submit(value):
        for button in value:
            print('---', button.path)

    fb.on_submit = on_submit

    app.run()
