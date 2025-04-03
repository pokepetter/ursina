import toml, os
from tkinter.font import Font
from types import SimpleNamespace

from .styles import Style

class Config:
    def __init__(self, master, config_file=None, darkmode=True, font=None, uifont=None):
        self.base = master
        self.dir = os.path.dirname(__file__)

        self.stipple = os.path.join(self.dir, 'stipple.xbm')
        if not config_file:
            config_file = os.path.join(self.dir, 'dark.toml') if darkmode else os.path.join(self.dir, 'light.toml')

        self.font = font or Font(family="Consolas", size=11)
        self.uifont = uifont or Font(family="Segoi UI", size=10)
        self.load_from(config_file)
    
    def load_from(self, config_file: str):
        self.theme = SimpleNamespace(**toml.load(config_file))
        self.theme.editor = SimpleNamespace(**self.theme.editor)
        self.theme.diffeditor = SimpleNamespace(**self.theme.diffeditor)
        self.syntax = self.theme.syntax

        self.style = Style(self.base, self)
