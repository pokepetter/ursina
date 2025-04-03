import re, codecs
import threading, queue
import tkinter as tk
from collections import deque

from .syntax import Syntax
from .highlighter import Highlighter
from .autocomplete import AutoComplete

from ..utils import Text


class Text(Text):
    def __init__(self, master, path=None, minimalist=False, language=None, autocomplete=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.path = path
        self.data = None
        self.encoding = 'utf-8'
        self.minimalist = minimalist
        
        self.buffer_size = 1000
        self.bom = True
        self.current_word = ""
        self.words = []
        self.active = False

        self.syntax = Syntax(self)
        if autocomplete is not None:
            self.auto_completion = autocomplete
        else:
            self.auto_completion = AutoComplete(
                self, items=self.syntax.get_autocomplete_list()) if not minimalist else None
        
        self.highlighter = Highlighter(self, language)

        self.focus_set()
        self.config_tags()
        self.create_proxy()
        self.config_bindings()
        self.configure(wrap=tk.WORD,relief=tk.FLAT, bg=self.base.theme.background, fg=self.base.theme.foreground, insertbackground=self.base.theme.cursor)

        self.update_words()

    def config_tags(self):
        self.tag_config(tk.SEL, background=self.base.theme.editor.selection)
        self.tag_config("highlight", background=self.base.theme.editor.currentword)
        self.tag_config("currentline", background=self.base.theme.editor.currentline)

        self.tag_config("found", background=self.base.theme.editor.found)
        self.tag_config("foundcurrent", background=self.base.theme.editor.foundcurrent)

    def config_bindings(self):
        self.bind("<KeyRelease>", self.key_release_events) 

        self.bind("<Control-f>", self.open_find_replace)
        self.bind("<Control-d>", self.multi_selection)
        self.bind("<Control-Left>", lambda e: self.handle_ctrl_hmovement())
        self.bind("<Control-Right>", lambda e: self.handle_ctrl_hmovement(True))

        self.bind("<Return>", self.enter_key_events)
        self.bind("<Tab>", self.tab_key_events)

        if self.minimalist:
            return

        self.bind("<FocusOut>", self.hide_autocomplete) 
        self.bind("<Button-1>", self.hide_autocomplete)
        self.bind("<Up>", self.auto_completion.move_up)
        self.bind("<Down>", self.auto_completion.move_down)

        # self.bind("<braceleft>", lambda e: self.complete_pair("}"))
        # self.bind("<bracketleft>", lambda e: self.complete_pair("]"))
        # self.bind("<parenleft>", lambda e: self.complete_pair(")"))

        # self.bind("<apostrophe>", lambda e: self.surrounding_selection("\'"))
        # self.bind("<quotedbl>", lambda e: self.surrounding_selection("\""))

    def key_release_events(self, event):
        if event.keysym not in ("Up", "Down", "Return"):
            self.show_autocomplete(event)

        match event.keysym:
            # autocompletion keys
            case "Button-2" | "BackSpace" | "Escape" | "Control_L" | "Control_R" | "space":
                self.hide_autocomplete()
            case "rightarrow" | "leftarrow":
                self.update_completions()
            
            # bracket pair completions
            case "braceleft":
                return self.complete_pair("}")
            case "bracketleft":
                return self.complete_pair("]")
            case "parenleft":
                return self.complete_pair(")")

            # surroundings for selection
            case "apostrophe":
                return self.surrounding_selection("\'")
            case "quotedbl":
                return self.surrounding_selection("\"")

            # extra spaces
            case ":" | ",":
                self.insert(tk.INSERT, " ")

            case _:
                pass

    def enter_key_events(self, *_):
        if not self.minimalist and self.auto_completion.active:        
            self.auto_completion.choose()
            return "break"
        
        return self.check_indentation()
        
    def tab_key_events(self, *_):
        if self.auto_completion.active:        
            self.auto_completion.choose()
            return "break"
    
        self.insert(tk.INSERT, " "*4)
        return "break"
    
    def get_all_text(self, *args):
        return self.get(1.0, tk.END)

    def get_all_text_ac(self, *args):
        """
        Helper function for autocomplete.show
        extracts all text except the current word.
        """
        return self.get(1.0, "insert-1c wordstart-1c") + self.get("insert+1c", tk.END)
    
    def get_current_word(self):
        return self.current_word.strip()
    
    def update_words(self, *_):
        if self.minimalist:
            return
        
        self.words = list(set(re.findall(r"\w+", self.get_all_text_ac())))
        self.after(1000, self.update_words)
    
    def update_completions(self):
        if self.minimalist:
            return
        
        self.auto_completion.update_completions()   
    
    def confirm_autocomplete(self, text):
        self.replace_current_word(text)
        
    def replace_current_word(self, new_word):
        if self.current_word.startswith("\n"):
            self.delete("insert-1c wordstart+1c", "insert")
        else:
            self.delete("insert-1c wordstart", "insert")
        self.insert("insert", new_word)
    
    def check_autocomplete_keys(self, event):
        """
        Helper function for autocomplete.show to check triggers
        """
        return True if event.keysym not in [
            "BackSpace", "Escape", "Return", "Tab", "space", 
            "Up", "Down", "Control_L", "Control_R"] else False 
    
    def cursor_screen_location(self):
        """
        Helper function for autocomplete.show to detect cursor location
        """
        pos_x, pos_y = self.winfo_rootx(), self.winfo_rooty()

        cursor = tk.INSERT
        bbox = self.bbox(cursor)
        if not bbox:
            return (0, 0)
        
        bbx_x, bbx_y, _, bbx_h = bbox
        return (pos_x + bbx_x - 1, pos_y + bbx_y + bbx_h)
    
    def hide_autocomplete(self, *_):
        if self.minimalist:
            return
        
        self.auto_completion.hide()
    
    def show_autocomplete(self, event):
        if self.minimalist or not self.check_autocomplete_keys(event):
            return

        if self.current_word.strip() not in ["{", "}", ":", "", None, "\""] and not self.current_word.strip()[0].isdigit():
            if not self.auto_completion.active:
                if event.keysym in ["Left", "Right"]:
                    return
                pos = self.cursor_screen_location()
                self.auto_completion.show(pos)
                self.auto_completion.update_completions()
            else:
                self.auto_completion.update_completions()
        else:
            if self.auto_completion.active:
                self.hide_autocomplete()

    def complete_pair(self, char):
        self.insert(tk.INSERT, char)
        self.mark_set(tk.INSERT, "insert-1c")
    
    def surrounding_selection(self, char):
        next_char = self.get("insert", "insert+1c")
        if next_char == char:
            self.mark_set(tk.INSERT, "insert+1c")
            self.delete("insert-1c", "insert")
            return "break"

        if self.tag_ranges(tk.SEL):
            self.insert(char, tk.SEL_LAST)
            self.insert(char, tk.SEL_FIRST)
            return
        
        self.complete_pair(char)
        return "break"

    def move_to_next_word(self):
        self.mark_set(tk.INSERT, self.index("insert+1c wordend"))

    def move_to_previous_word(self):
        self.mark_set(tk.INSERT, self.index("insert-1c wordstart"))

    def handle_ctrl_hmovement(self, delta=False):
        if delta:
            self.move_to_next_word()
        else:
            self.move_to_previous_word()
        
        return "break"

    def update_current_indent(self):
        line = self.get("insert linestart", "insert lineend")
        match = re.match(r'^(\s+)', line)
        self.current_indent = len(match.group(0)) if match else 0

    def update_current_line(self):
        self.current_line = self.get("insert linestart", "insert lineend")
        return self.current_line
    
    def add_newline(self, count=1):
        self.insert(tk.INSERT, "\n" * count)
    
    def check_indentation(self, *args):
        self.update_current_indent()
        if self.update_current_line():
            if self.current_line[-1] in ["{", "[", ":", "("]:
                self.current_indent += 4
            elif self.current_line[-1] in ["}", "]", ")"]:
                self.current_indent -= 4
            
            self.add_newline()
            self.insert(tk.INSERT, " " * self.current_indent)

            self.update_current_indent()
            
            return "break"

    def multi_selection(self, *args):
        #TODO: multi cursor editing
        return "break"

    def open_find_replace(self, *_):
        self.base.findreplace.show(self)

    def detect_encoding(self, file_path):
        with open(file_path, 'rb') as file:
            bom = file.read(4)

        if bom.startswith(codecs.BOM_UTF8):
            return 'utf-8'
        elif bom.startswith(codecs.BOM_LE) or bom.startswith(codecs.BOM_BE):
            return 'utf-16'
        elif bom.startswith(codecs.BOM32_BE) or bom.startswith(codecs.BOM32_LE):
            return 'utf-32'

        self.bom = False
        return 'utf-8'

    def load_file(self):
        try:
            encoding = self.detect_encoding(self.path)
            file = open(self.path, 'r', encoding=encoding)
            self.encoding = encoding

            self.queue = queue.Queue()
            threading.Thread(target=self.read_file, args=(file,)).start()
            self.process_queue()
        except Exception as e:
            self.master.master.unsupported_file()

    def read_file(self, file):
        while True:
            chunk = file.read(self.buffer_size)
            if not chunk:
                file.close()
                self.queue.put(None)  # Signal the end of reading
                break
            self.queue.put(chunk)

    def process_queue(self):
        try:
            while True:
                chunk = self.queue.get_nowait()
                if chunk is None:
                    self.master.master.on_change()
                    self.master.master.on_scroll()
                    break
                self.write(chunk)
                self.update()
                self.master.master.on_scroll()
        except queue.Empty:
            # If the queue is empty, schedule the next check after a short delay
            self.master.master.after(100, self.process_queue)
    
    def save_file(self, path=None):
        if path:
            try:
                with open(path, 'w') as fp:
                    fp.write(self.get_all_text())
            except Exception:
                return
            
            self.path = path
        try:
            with open(self.path, 'w') as fp:
                fp.write(self.get_all_text())
        except Exception:
            return
             
    def copy(self, *_):
        self.event_generate("<<Copy>>")

    def cut(self, *_):
        self.event_generate("<<Cut>>")
    
    def paste(self, *_):
        self.event_generate("<<Paste>>")

    def set_data(self, data):
        self.data = data
        
    def clear(self):
        self.delete(1.0, tk.END)

    def write(self, text, *args):
        self.insert(tk.END, text, *args)
    
    def newline(self, *args):
        self.write("\n", *args)
    
    def get_all_text(self):
        return self.get(1.0, tk.END)
    
    def get_selected_text(self):
        try:
            return self.selection_get()
        except Exception:
            return ""
        
    def add_newline(self, count=1):
        self.insert(tk.INSERT, "\n" * count)

    def get_selected_count(self):
        return len(self.get_selected_text())
        
    @property
    def line(self):
        return int(self.index(tk.INSERT).split('.')[0])
    
    @property
    def column(self):
        return int(self.index(tk.INSERT).split('.')[1]) + 1

    @property
    def position(self):
        lc = self.index(tk.INSERT).split('.')
        return [lc[0], int(lc[1]) + 1]

    def scroll_to_end(self):
        self.mark_set(tk.INSERT, tk.END)
        self.see(tk.INSERT)
    
    def scroll_to_start(self):
        self.mark_set(tk.INSERT, 1.0)
        self.see(tk.INSERT)
    
    def scroll_to_line(self, line):
        self.mark_set(tk.INSERT, line)
        self.see(tk.INSERT)
    
    def set_wrap(self, flag=True):
        if flag:
            self.configure(wrap=tk.WORD)
        else:
            self.configure(wrap=tk.NONE)
    
    def set_active(self, flag=True):
        if flag:
            self.configure(state=tk.NORMAL)
        else:
            self.configure(state=tk.DISABLED)
    
    def show_unsupported_dialog(self):
        self.set_wrap(True)
        self.configure(font=('Arial', 10), padx=10, pady=10)
        self.write("This file is not displayed in this editor because it is either binary or uses an unsupported text encoding.")
        self.set_active(False)

    def move_cursor(self, position):
        self.mark_set(tk.INSERT, position)

    def clear_all_selection(self):
        self.tag_remove(tk.SEL, 1.0, tk.END)

    def highlight_current_line(self, *_):
        self.tag_remove("currentline", 1.0, tk.END)
        if self.get_selected_text():
            return
        
        line = int(self.index(tk.INSERT).split(".")[0])
        start = str(float(line))
        end = str(float(line + 1))
        self.tag_add("currentline", start, end)

    def select_line(self, line):
        self.clear_all_selection()
        
        line = int(line.split(".")[0])
        start = str(float(line))
        end = str(float(line + 1))
        self.tag_add(tk.SEL, start, end)

        self.move_cursor(end)
    
    def highlight_current_word(self):
        if self.minimalist or self.get_selected_text():
            return

        self.tag_remove("highlight", 1.0, tk.END)
        word = re.findall(r"\w+", self.get("insert wordstart", "insert wordend"))
        if any(word) and word[0] not in self.syntax.keywords:
            self.highlight_pattern(f"\\y{word[0]}\\y", "highlight", regexp=True)

        # elif word := self.get_selected_text():
        #     self.highlight_pattern(word, "highlight", end="sel.first")
        #     self.highlight_pattern(word, start="sel.last")


    def highlight_pattern(self, pattern, tag, start="1.0", end=tk.END, regexp=False):
        start = self.index(start)
        end = self.index(end)
        
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        self.tag_remove(tag, start, end)
        
        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit", count=count, regexp=regexp)
            if index == "" or count.get() == 0:
                break

            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", f"{index}+{count.get()}c")

            self.tag_add(tag, "matchStart", "matchEnd")

    def refresh(self, *args):
        if self.minimalist:
            return
        
        if self.active :
            self.current_word = self.get("insert-1c wordstart", "insert")
            if self.current_word is None:
                self.current_word = ""
            self.highlighter.highlight()
            self.highlight_current_line()
            self.highlight_current_word()

    def create_proxy(self):
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

        if (args[0] in ("insert", "replace", "delete") or args[0:3] == ("mark", "set", "insert")):
            self.event_generate("<<Change>>", when="tail")
        
        elif (args[0:2] == ("xview", "moveto") or args[0:2] == ("yview", "moveto") or 
              args[0:2] == ("xview", "scroll") or args[0:2] == ("yview", "scroll")):
            self.event_generate("<<Scroll>>", when="tail")
            
        return result
