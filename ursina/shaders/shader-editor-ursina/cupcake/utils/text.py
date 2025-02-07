import tkinter as tk


class Text(tk.Text):
    """
    normal text with reference to base
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.base = master.master.base
