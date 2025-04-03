import tkinter.ttk as ttk
import tkinter as tk

from .scrollbar import Scrollbar
from .frame import Frame


class Tree(Frame):
    instance=0
    def __init__(self, master, path=None, doubleclick=lambda _: None, singleclick=lambda _: None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.instance = Tree.instance
        self.config(bg=self.base.theme.tree["background"])


        self.path = path
        self.doubleclick = doubleclick
        self.singleclick = singleclick

        self.tree = ttk.Treeview(self, show="tree", columns=("fullpath", "type"), 
                                 displaycolumns='', selectmode=tk.BROWSE)
        self.tree.pack(side=tk.TOP, fill=tk.X)
        
        self.scrollbar = Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview, style=f"TreeScrollbar{self.instance}")
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.tree.yview)
        
        self.tree.bind("<Double-Button-1>", self.doubleclick)
        self.tree.bind("<<TreeviewSelect>>", self.check_singleclick)
        Tree.instance += 1

    def check_singleclick(self, _):
        if self.item_type(self.focus()) == 'file':
            if self.singleclick:
                self.singleclick(self.item_fullpath(self.focus()))
        else:
            self.toggle_node(self.focus())
    
    def clear_node(self, node):
        self.tree.delete(*self.tree.get_children(node))

    def clear_tree(self):
        self.clear_node('')

    def collapse_all(self):
        for node in self.tree.get_children():
            self.tree.item(node, open=False)
    
    def delete(self, *a, **kw):
        self.tree.delete(*a, *kw)
    
    def focus(self):
        return self.tree.focus()

    def get_children(self, *a, **kw):
        return self.tree.get_children(*a, **kw)

    def insert(self, *args, **kwargs):
        return self.tree.insert(*args, **kwargs)
        
    def is_open(self, node):
        return self.tree.item(node, "open")
    
    def item(self, *a, **kw):
        return self.tree.item(*a, **kw)
        
    def item_type(self, item):
        return self.set(item, "type")
    
    def item_fullpath(self, item):
        return self.set(item, "fullpath")

    def selected_path(self):
        return self.item_fullpath(self.focus())

    def selected_type(self):
        return self.item_type(self.focus())

    def set(self, *args, **kwargs):
        return self.tree.set(*args, **kwargs)

    def toggle_node(self, node):
        if self.item_type(node) == 'directory':
            if self.is_open(node):
                self.tree.item(node, open=False)
            else:
                self.tree.item(node, open=True)
