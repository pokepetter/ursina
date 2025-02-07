__version__ = '0.25.8'
__version_info__ = tuple([ int(num) for num in __version__.split('.')])

__all__ = ["Editor", "get_editor", "DiffEditor", "ImageViewer", "TextEditor", "Config", "Languages"]


import os
import tkinter as tk
from tkinter.font import Font

from .config import Config
from .languages import Languages
from .utils import FileType, Frame

from .breadcrumbs import BreadCrumbs
from .diffeditor import DiffEditor
from .imageviewer import ImageViewer
from .texteditor import TextEditor

def get_editor(base, path=None, path2=None, diff=False, language=None, autocomplete=None):
    "picks the right editor for the given values"
    if diff:
        return DiffEditor(base, path, path2, language=language)
    
    if path and os.path.isfile(path):
        if FileType.is_image(path):
            return ImageViewer(base, path)
        
        return TextEditor(base, path, language=language, autocomplete=autocomplete)
    
    return TextEditor(base, language=language, autocomplete=autocomplete)


class Editor(Frame):
    """
    Editor class
    Picks the right editor based on the path, path2, diff values passed. Supports showing diff, images, text files. 
    If nothing is passed, empty text editor is opened. 
    
    Attributes
    ----------
    path : str
        path of the file to be opened
    path2 : str
        path of file to be opened in diff, required if diff=True is passed
    diff : bool
        whether this is to be opened in diff editor
    language : str
        Use the `Languages` enum provided (eg. Languages.PYTHON, Languages.TYPESCRIPT)
        This is given priority while picking suitable highlighter. If not passed, guesses from file extension.
    dark_mode : str
        Sets the editor theme to cupcake dark if True, or cupcake light by default
        This is ignored if custom config_file path is passed
    config_file : str
        path to the custom config (TOML) file, uses theme defaults if not passed
    showpath : bool
        whether to show the breadcrumbs for editor or not
    font : str | Font
        Font used in line numbers, text editor, autocomplete. defaults to Consolas(11)
    uifont : str | Font
        Font used for other UI components (breadcrumbs, trees)
    preview_file_callback : function(path)
        called when files in breadcrumbs-pathview are single clicked. MUST take an argument (path)
    open_file_callback : function(path)
        called when files in breadcrumbs-pathview are double clicked. MUST take an argument (path)

    NOTE: All the *tk.Text* methods are available under *Editor.content* (eg. Editor.content.insert, Editor.content.get)

    Methods
    -------
    save(path: str=None)
        If the content is editable writes to the specified path.
    focus()
        Gives focus to the content.
    """
    def __init__(self, master, 
                 path: str=None, path2: str=None, diff: bool=False, language: str=None,
                 darkmode=True, config_file: str=None, showpath: bool=True, 
                 font: str|Font=None, uifont: str|Font=None,
                 preview_file_callback=None, open_file_callback=None,
                 autocomplete = None,
                 *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

        self.path2 = path2
        self.diff = diff
        self.showpath = showpath
        self.darkmode = darkmode
        self.config_file = config_file
        self.preview_file_callback = preview_file_callback
        self.open_file_callback = open_file_callback

        self.settings = Config(self, config_file, darkmode, font, uifont)
        self.theme = self.settings.theme

        self.config(bg=self.theme.border)

        self.content = get_editor(self, path, path2, diff, language, autocomplete)
        self.content.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.path = path
        self.pack_propagate(False)
    
    def save(self, path: str=None) -> None:
        self.content.save(path)
    
    def focus(self) -> None:
        self.content.focus()

    def configure(self, **kwargs) -> None:
        if "path" in kwargs:
            self.path = kwargs.pop("path")
        super().configure(**kwargs)
    
    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        self._path = value
        if hasattr(self,"content"):
            self.content.path = value
            self.content.update()
        if value:
            self.filename = os.path.basename(value) if value else None
            if self.showpath and not self.diff:
                if hasattr(self, "breadcrumbs"):
                    self.breadcrumbs.path = value
                    self.breadcrumbs.update()
                else:
                    self.breadcrumbs = BreadCrumbs(self, value)
                    self.breadcrumbs.pack(side=tk.TOP, fill=tk.X)
                self.content.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        else:
            if hasattr(self, "breadcrumbs"):
                self.breadcrumbs.pack_forget()
            self.filename = None
            self.content.pack(side=tk.TOP, fill=tk.BOTH, expand=True)