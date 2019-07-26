from ursina import *
from ursina.prefabs.file_browser import FileBrowser


class FileBrowserSave(FileBrowser):
    def __init__(self, **kwargs):
        super().__init__()

        self.save_button = self.open_button
        self.save_button.color = color.azure
        self.save_button.text = 'Save'
        self.save_button.on_click = self.save
        self.file_name_field = InputField(
            parent = self,
            scale_x = .75,
            scale_y = self.save_button.scale_y,
            y = self.save_button.y,
            active = True,
            )
        # self.file_name_field.text_field.scale *= .6
        self.save_button.y -= .075
        self.cancel_button.y -= .075
        self.file_name_field.text_field.text = ''
        self.file_type = '' # to save as

        self.data = ''

        for key, value in kwargs.items():
            setattr(self, key ,value)



    def save(self):
        file_name = self.file_name_field.text_field.text
        if not file_name.endswith(self.file_type):
            file_name += self.file_type

        p = self.path / file_name
        print('save:', p)
        if p.exists():
            print('overwrite file?')
            return

        else:
            if isinstance(self.data, str):
                p.write_text(self.data)
            else:
                print('write bytes')
                p.write_bytes(self.data)

            self.close()




if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    FileBrowserSave(file_type = '.oto')
    app.run()
