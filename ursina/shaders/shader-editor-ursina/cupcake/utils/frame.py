import tkinter as tk


class Frame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        try:
            self.base = master.base
        except:
            self.base = self
