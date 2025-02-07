import tkinter as tk
from .breakpoint import Breakpoint
from ...utils import Canvas, Menubutton


class LineNumbers(Canvas):
    def __init__(self, master, text=None, font=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.font = font

        self.fg = self.base.theme.linenumbers["foreground"]
        self.hfg = self.base.theme.linenumbers["activeforeground"]

        self.config(width=65, bd=0, highlightthickness=0, bg=self.base.theme.linenumbers["background"])
        self.text = text

    def attach(self, text):
        self.text = text
    
    def mark_line(self, line):
        dline = self.text.dlineinfo(line)
        
        if not dline:
            return
        
        y = dline[1]
        btn = Menubutton(self, 
            text=">", font=self.font, cursor="hand2", borderwidth=0,
            width=2, height=1, pady=0, padx=0, relief=tk.FLAT, **self.base.theme.linenumbers)
        self.create_window(70, y-2, anchor=tk.NE, window=btn)
    
    def set_bar_width(self, width):
        self.configure(width=width)
        
    def get_indentation_level(self, line):
        """Get the indentation level of a given line."""
        return len(line) - len(line.lstrip())

    def redraw(self, *_):
        self.delete(tk.ALL)

        prev_indent = 0
        i = self.text.index("@0,0")
        while True:
            dline = self.text.dlineinfo(i)
            if dline is None:
                break

            y = dline[1]
            linenum = str(i).split(".")[0]

            # Get the text content of the current line
            line_content = self.text.get(f"{linenum}.0", f"{linenum}.end")
            current_indent = self.get_indentation_level(line_content)

            # to highlight the current line
            curline = self.text.dlineinfo(tk.INSERT)
            cur_y = curline[1] if curline else None

            if not cur_y:
                i = self.text.index(f"{i}+1line")
                continue

            self.create_text(40, y, anchor=tk.NE, text=linenum, font=self.font, tag=i, fill=self.hfg if y == cur_y else self.fg)
            self.tag_bind(i, "<Button-1>", lambda _, i=i: self.text.select_line(i))

            """
            if current_indent > prev_indent:
                self.create_text(50, y, anchor=tk.NW, text="+", font=self.font, fill=self.fg, tag=f"f{i}")
                self.tag_bind(f"f{i}", "<Button-1>", lambda _, i=i: print(f"Fold from {i}"))
            """
            
            # Update the previous indentation level
            prev_indent = current_indent
            i = self.text.index(f"{i}+1line")

    def draw_breakpoint(self, y):
        bp = Breakpoint(self)
        self.create_window(21, y-2, anchor=tk.NE, window=bp)
