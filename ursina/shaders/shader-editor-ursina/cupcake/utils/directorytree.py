import os
import tkinter as tk

from .frame import Frame
from .tree import Tree


class DirectoryTree(Frame):
    def __init__(self, master, path=None, openfile=None, preview_file=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.openfile = openfile
        self.preview_file = preview_file

        self.nodes = {}
        
        self.ignore_dirs = [".git", "__pycache__"]
        self.ignore_exts = [".pyc"]

        self.tree = Tree(self, path, doubleclick=self.openfile, singleclick=self.preview_file, *args, **kwargs)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.path = path
        if path:
            self.change_path(path)
        else:
            self.tree.insert('', 0, text='You have not yet opened a file.')
        self.tree.tree.bind("<<TreeviewOpen>>", self.on_treeview_open)
        
    def change_path(self, path):
        self.nodes.clear()
        self.path = path
        if self.path:
            self.tree.clear_tree()
            self.create_root()
        else:
            self.tree.clear_tree()
            self.tree.insert('', 0, text='Empty')
        
    def create_root(self):
        self.update_treeview([(p, os.path.join(self.path, p)) for p in os.listdir(self.path)])

        for path, item in list(self.nodes.items()):
            if not os.path.exists(path):
                self.tree.delete(item)
                self.nodes.pop(path)

    def get_actionset(self):
        return self.actionset
    
    def scandir(self, path):
        entries = []
        for entry in os.scandir(path):
            entries.append((entry.name, entry.path))
        return entries

    def update_treeview(self, entries, parent=""):
        entries.sort(key=lambda x: (not os.path.isdir(x[1]), x[0]))
        for name, path in entries:
            if os.path.isdir(path):
                if name in self.ignore_dirs:
                    continue

                item = self.tree.tree.insert(parent, "end", text=f"  {name}", values=[path, 'directory'], image='foldericon', open=False)
                self.tree.tree.insert(item, "end", text="loading...")
                self.tree.tree.update_idletasks()
            else:
                if name.split(".")[-1] in self.ignore_exts:
                    continue

                #TODO check filetype and get matching icon, cases
                item = self.tree.tree.insert(parent, "end", text=f"  {name}", values=[path, 'file'], image='document')
                self.tree.tree.update_idletasks()

    def on_treeview_open(self, event):
        item_id = self.tree.tree.focus()
        if not item_id:
            return

        path = self.tree.tree.item(item_id, "values")[0]
        if not path or not os.path.isdir(path):
            return

        parent_id = item_id
        self.tree.tree.delete(*self.tree.tree.get_children(parent_id))
        self.update_treeview(self.scandir(path), parent_id)

    def close_directory(self):
        self.change_path(None)
    
    def openfile(self, _):
        if self.openfile:
            self.openfile()
    
    def preview_file(self, *_):
        if self.preview_file:
            self.preview_file()
