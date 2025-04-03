from .utils import Frame


class BaseEditor(Frame):
    """
    Base class for editors.
    """
    def __init__(self, master, path=None, path2=None, editable=True, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(bg=self.base.theme.background)

        self.path = path
        self.path2 = path2
        self.editable = editable

        self.showpath = False
        self.content = None
        self.diff = False

    def save(self, *_):
        ...
