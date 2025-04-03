from ursina import *
from ursina.prefabs.file_browser import FileBrowser, FileButton


class FileButtonSave(FileButton):
    def on_click(self):
        if len([e for e in self.parent.children if e.selected]) >= self.load_menu.selection_limit and not self.selected:
            for e in self.parent.children:  # clear selection
                e.selected = False

        self.selected = True
        self.load_menu.file_name_field.text = str(self.path.name)


    def on_double_click(self):
        if self.path.is_dir():
            self.load_menu.path = self.path
        else:
            self.selected = True
            self.load_menu.open()


@generate_properties_for_class()
class FileBrowserSave(FileBrowser):
    def __init__(self, **kwargs):
        super().__init__(file_button_class=FileButtonSave)

        self.save_button = self.open_button
        self.save_button.color = color.azure
        self.save_button.text = 'Save'
        self.save_button.on_click = self._save
        self.file_name_field = InputField(parent=self, scale_x=.75, scale_y=self.save_button.scale_y, y=self.save_button.y)
        self.save_button.y -= .075
        self.cancel_button.y -= .075
        self.file_name_field.text_field.text = ''
        self.file_type = '' # to save as

        self.last_saved_file = None     # gets set when you save a file
        self.overwrite_prompt = WindowPanel(
            content=(
                Text('Overwrite?'),
                Button('Yes', color=color.azure, on_click=self._save),
                Button('Cancel')
            ), z=-1, popup=True, enabled=False)

        for key, value in kwargs.items():
            setattr(self, key ,value)


    def file_type_setter(self, value):
        self._file_type = value
        self.file_types = (value, )


    def on_enable(self):
        super().on_enable()
        self.file_name_field.active = True

    def on_disable(self):
        self.file_name_field.active = False


    def _save(self):
        file_name = self.file_name_field.text_field.text
        if not file_name.endswith(self.file_type):
            file_name += self.file_type

        path = self.path / file_name
        # print('save:', path)
        if path.exists() and not self.overwrite_prompt.enabled:
            # print('overwrite file?')
            self.overwrite_prompt.enabled = True

        self.last_saved_file = path
        self.overwrite_prompt.enabled = False
        self.close()
        self.on_submit(path)


    def on_submit(self, path):  # implement .on_submit to handle saving
        print('save to path:', path, 'please implement .on_submit to handle saving')



if __name__ == '__main__':
    from ursina import *
    from ursina.prefabs.file_browser_save import FileBrowserSave

    app = Ursina()
    wp = FileBrowserSave(file_type = '.*')


    import json
    save_data = {'level': 4, 'name':'Link'}
    wp.data = json.dumps(save_data)

    wp.enabled = False
    def input(key):
        if key == 'tab':
            wp.enabled = not wp.enabled


    app.run()
