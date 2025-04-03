from ..texteditor import TextEditor

# TODO currently using TextEditor, use Editor instead
class DiffPane(TextEditor):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, minimalist=True, *args, **kwargs)

    def load_file(self):
        self.text.load_file()
    
    def load_text(self, text):
        self.text.clear_insert(text)
