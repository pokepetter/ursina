from ..utils import DirectoryTree, Toplevel


class PathView(Toplevel):
    def __init__(self, master, width=150, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.width = round(width)
        
        self.tree = DirectoryTree(self, width=width)
        self.tree.pack()

        self.config(bg=self.base.theme.border)
        self.overrideredirect(True)
        self.withdraw()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.configure_bindings()

    def configure_bindings(self):
        self.bind("<FocusOut>", self.hide)
        self.bind("<Escape>", self.hide)
    
    def get_popup_x(self, width):
        return self.winfo_rootx() + int(self.winfo_width() / 2) - int(width / 2)

    def get_popup_y(self):
        return self.winfo_rooty()
    
    def hide(self, *_):
        self.withdraw()
        
    def show(self, e):
        self.update_idletasks()
        w = e.widget
        x = w.winfo_rootx()
        y = w.winfo_rooty() + w.winfo_height()
        
        if not w.path:
            return
        self.tree.change_path(w.path)

        self.geometry(f"+{x}+{y}")
        self.deiconify()
        self.focus_set()
