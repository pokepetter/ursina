import tkinter as tk
from itertools import chain

from .kinds import Kinds
from .item import AutoCompleteItem

from ...utils import Toplevel


class AutoComplete(Toplevel):
    def __init__(self, master, items=None, active=False, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.autocomplete_kinds = Kinds(self)
        self.config(padx=1, pady=1, bg=self.base.theme.border)
        
        self.active = active
        if not self.active:
            self.withdraw()
        
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.grid_columnconfigure(0, weight=1)

        self.menu_items = []
        self.active_items = []
        self.row = 0
        self.selected = 0
        if items:
            # TODO this should be a dict
            self.items = items # [(completion, type), ...]
            self.add_all_items()
            self.refresh_selected()
    
    def update_completions(self):
        self.refresh_geometry()
        self.update_idletasks()
        self.update_all_words()

        term = self.master.get_current_word()

        exact, starts, includes = [], [], []
        for i in self.menu_items:
            if i.get_text() == term:
                exact.append(i)
            elif i.get_text().startswith(term):
                starts.append(i)
            elif term in i.get_text():
                includes.append(i)
        new = list(chain(exact, starts, includes))

        self.hide_all_items()
        if any(new):
            self.show_items(new[:10] if len(new) > 10 else new, term)
        else:
            self.hide()
    
    def move_up(self, *_):
        if self.active:
            self.select(-1)
            return "break"
    
    def move_down(self, *_):
        if self.active:
            self.select(1)
            return "break"

    def add_all_items(self):
        for i in self.items:
            self.add_item(i[0], i[1] if len(i) > 1 else None) 
            
        self.active_items = self.menu_items
        self.refresh_selected()
    
    def update_all_words(self):
        for word in self.master.words:
            if word not in self.get_items_text():
                self.add_item(word, "word")
        
        for word in self.menu_items:
            if word.get_text() not in self.master.words and word.get_kind() == "word":
                self.remove_item(word)

    def add_item(self, text, kind=None):
        new_item = AutoCompleteItem(self, text, kind=kind)
        new_item.grid(row=self.row, sticky=tk.EW)
        
        self.menu_items.append(new_item)

        self.row += 1
    
    def remove_item(self, item):
        a = self.menu_items
        item.grid_forget()
        self.menu_items.remove(item)
        self.row -= 1

    def select(self, delta):
        self.selected += delta
        if self.selected > len(self.active_items) - 1:
            self.selected = 0
        elif self.selected < 0:
            self.selected = len(self.active_items) - 1
        self.refresh_selected()
    
    def reset_selection(self):
        self.selected = 0
        self.refresh_selected()

    def refresh_selected(self):
        for i in self.active_items:
            i.deselect()
        if self.selected < len(self.active_items):
            self.active_items[self.selected].select()
    
    def get_items_text(self):
        return [i.get_text() for i in self.menu_items]
    
    def hide_all_items(self):
        for i in self.menu_items:
            i.grid_forget()
        
        self.active_items = []
        self.row = 1
    
    def show_items(self, items, term):
        self.active_items = items
        for i in items:
            i.grid(row=self.row, sticky=tk.EW)
            self.row += 1

            i.mark_term(term)

        self.reset_selection()
    
    def refresh_geometry(self, *_):
        self.update_idletasks()
        self.geometry("+{}+{}".format(*self.master.cursor_screen_location()))

    def show(self, pos):
        self.active = True
        self.update_idletasks()
        self.geometry("+{}+{}".format(*pos))
        self.deiconify()

    def hide(self, *_):
        self.active = False
        self.withdraw()
        self.reset()
    
    def reset(self):
        self.reset_selection()
    
    def choose(self, this=None, *_):
        if not self.active_items:
            return
        
        if not this:
            this = self.active_items[self.selected]
        
        self.master.confirm_autocomplete(this.get_text())
        self.hide()
        return "break"

    def updateMaster(self, master):
        self.master = master
        self.autocomplete_kinds.master = master