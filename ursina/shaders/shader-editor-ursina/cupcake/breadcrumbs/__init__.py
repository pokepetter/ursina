import os
import tkinter as tk
from .pathview import PathView

from ..utils import Frame, Menubutton


class Item(Menubutton):
    def __init__(self, master, path, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.path = path
        self.config(pady=3, padx=3, font=self.base.settings.uifont, **self.base.theme.breadcrumbs)

class BreadCrumbs(Frame):
    def __init__(self, master, path=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(padx=20, bg=self.base.theme.breadcrumbs["background"])
        self.config(width=master.winfo_width()-40)
        self.pathview = PathView(self)
        path = os.path.abspath(path).split('\\')
        for i, item in enumerate(path):
            text = item if item == path[-1] else f"{item} ›"
            self.additem("\\".join(path[:i]), text)

    def additem(self, path, text):
        btn = Item(self, path, text=text)
        btn.bind("<Button-1>", self.pathview.show)
        btn.pack(side=tk.LEFT)
