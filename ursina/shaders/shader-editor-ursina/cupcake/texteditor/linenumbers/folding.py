import tkinter as tk
from tkinter import INSERT, NE, Canvas, Menubutton
from tkinter.font import Font


class LineNumbers(Canvas):
    def __init__(self, master, text=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(width=50, bd=0, highlightthickness=0)
        self.text = text
        self.text.config(bd=0, highlightthickness=0)
        self.text.tag_config("sel", background="#48484f", foreground="#e1e1e6")
        self.text.bind("<Configure>", self.redraw)
        self.text.bind("<<Change>>", self.redraw)

    def attach(self, text):
        self.text = text

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

            # Determine if the current line has more indentation than the previous line
            if current_indent > prev_indent:
                line_num_with_indent = f"+ {linenum}"
            elif current_indent < prev_indent:
                line_num_with_indent = f"- {linenum}"
            else:
                line_num_with_indent = linenum

            # to highlight the current line
            curline = self.text.dlineinfo(tk.INSERT)
            cur_y = curline[1] if curline else None

            if not cur_y:
                i = self.text.index(f"{i}+1line")
                continue

            if y == cur_y:
                self.create_text(40, y, anchor=tk.NE, text=line_num_with_indent, font=("Consolas", 14), fill="#83838f", tag=i)
            else:
                self.create_text(40, y, anchor=tk.NE, text=line_num_with_indent, font=("Consolas", 14), fill="#525259", tag=i)

            
            # Update the previous indentation level
            prev_indent = current_indent
            i = self.text.index(f"{i}+1line")

class Text(tk.Text):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.mark_set('input', 'insert')
        self.mark_gravity('input', 'left')

        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        
    def _proxy(self, *args):
        if args[0] == 'get' and (args[1] == tk.SEL_FIRST and args[2] == tk.SEL_LAST) and not self.tag_ranges(tk.SEL): 
            return
        if args[0] == 'delete' and (args[1] == tk.SEL_FIRST and args[2] == tk.SEL_LAST) and not self.tag_ranges(tk.SEL): 
            return

        cmd = (self._orig,) + args
        result = self.tk.call(cmd)

        if (args[0] in ("insert", "replace", "delete") or args[0:3] == ("mark", "set", "insert") 
            or args[0:2] == ("xview", "moveto") or args[0:2] == ("yview", "moveto") 
            or args[0:2] == ("xview", "scroll") or args[0:2] == ("yview", "scroll")):
            self.event_generate("<<Change>>", when="tail")
            
        return result


class ExampleApp:
    def __init__(self, root):
        self.font = ("Consolas", 14)

        self.text_widget = Text(root, wrap=tk.NONE, font=self.font, bg="#2e2e32", fg="#e1e1e6")
        self.line_numbers = LineNumbers(root, text=self.text_widget, bg="#2e2e32")

        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Sample text with indentation for testing code folding
        sample_code = """\
def foo():
    print("Hello,")
    print("World!")
    if True:
        print("This is a nested block.")
    print("Indented lines are foldable.")
print("Code folding based on indentation.")
"""
        self.text_widget.insert(tk.END, sample_code)
        self.line_numbers.redraw()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExampleApp(root)
    root.mainloop()