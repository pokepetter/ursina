from ursina import *


class FileButton(Button):
    def __init__(self, **kwargs):
        super().__init__(
            hovered_color = color.orange,
            scale = (.5,.025),
            selected = False,
            )

        for key, value in kwargs.items():
            setattr(self, key, value)


    def on_click(self):
        if len(self.load_menu.selection) >= self.load_menu.selection_limit:
            for e in self.load_menu.selection:
                e.selected = False

        self.selected = not self.selected
        if self.selected:
            self.load_menu.address_bar.text = str(self.path.resolve())


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
            self.color = color.yellow
        else:
            self.color = Button.color



class FileBrowser(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, scale=(1,1), model='quad', color=color.clear, collider='box', y=.45)

        self.title_bar = Button(parent=self, scale=(.75,.025), text='Open', color=color.amvol_color, collision=False)
        self.folder_up_button = Button(parent=self, scale=(.035,.035), text='^', position=(-.4,-.03), on_click=self.folder_up)
        self.address_bar = InputField(parent=self, y=-.03, scale=(.75,.035), text_origin=(-.5,0))
        self.button_parent = Entity(parent=self)
        self.bg = Button(parent=self, z=1, scale=(999,999), color=color.black66, highlight_color=color.black66, pressed_color=color.black66)

        self.return_files = True
        self.return_directories = False
        self.selection_limit = 1
        self.max_buttons = 24

        self.cancel_buttn = Button(parent=self, scale=(.5*.24, .05), y=(-self.max_buttons*.025)-.15, origin_x=-.5, x=-.25, text='Cancel', on_click=self.close)
        self.open_button = Button(parent=self, scale=(.5*.74, .05), y=(-self.max_buttons*.025)-.15, origin_x=.5, x=.25, text='Open', color=color.amvol_color, on_click=self.open)

        self.file_types = ['.*', ]
        self.start_path = Path('.').resolve()

        for key, value in kwargs.items():
            setattr(self, key ,value)


        self.path = self.start_path     # this will populate the list
        self.scroll = 0


    def input(self, key):
        if key == 'scroll down':
            if self.scroll + self.max_buttons < len(self.button_parent.children)-1:
                self.scroll += 1
                self.button_parent.y += .025

        if key == 'scroll up':
            if self.scroll > 0:
                self.scroll -= 1
                self.button_parent.y -= .025

    @property
    def scroll(self):
        return self._scroll

    @scroll.setter
    def scroll(self, value):
        self._scroll = value

        for i, c in enumerate(self.button_parent.children):
            c.enabled = i >= value
            if i > value + self.max_buttons:
                c.enabled = False


    @property
    def path(self):
        return self._path


    @path.setter
    def path(self, value):
        self._path = value
        self.address_bar.text = str(value.resolve())

        for c in self.button_parent.children:
            destroy(c)

        files = [e for e in value.iterdir() if e.is_dir() or e.suffix in self.file_types or '.*' in self.file_types]
        files.sort(key=lambda x : x.is_file())  # directories first

        for i, f in enumerate(files):
            prefix = ' '
            if f.is_dir():
                prefix = ' [_] '

            b = FileButton(
                parent = self.button_parent,
                text = prefix + f.name,
                text_origin = (-.5, 0),
                y = -i*.025 -.1,
                load_menu = self,
                path = f,
                )

        self.scroll = self.scroll

    def on_enable(self):
        self.scale = 1
        self.bg.enabled = True
        self.path = self.path

    def close(self):
        self.bg.enabled = False
        self.animate_scale_y(0, duration=.1)
        invoke(setattr, self, 'enabled', False, delay=.2)


    def folder_up(self):
        self.path = self.path.parent

    def open(self):
        if len(self.selection) == 1 and self.selection[0].path.is_dir():
            self.path = self.selection[0].path
            return

        if hasattr(self, 'on_submit'):
            self.on_submit(self.selection)

        self.close()


    @property
    def selection(self):
        return [c for c in self.button_parent.children if c.selected == True]




if __name__ == '__main__':
    app = Ursina()
    panel_color =   color.color(32,.2,.25)
    record_color =  color.color(0,.68,.62)
    color.yellow =  color.color(31,.68,.62)
    color.violet =  color.color(292,.68,.62)
    Button.color =  color.color(22,.48,.42)
    amvol_color =   color.color(56,.28,.38)

    color.amvol_color = amvol_color
    color.panel_color = panel_color
    color.record_color = record_color

    FileBrowser(file_types=('.*'))
    app.run()
