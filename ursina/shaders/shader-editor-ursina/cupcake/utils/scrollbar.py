from tkinter import ttk
import tkinter as tk

class Scrollbar(ttk.Scrollbar):
    def set(self, low, high):
        if float(low) <= 0.0 and float(high) >= 1.0:
            self.pack_forget()
        else:
            self.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Scrollbar.set(self, low, high)
