import os, tkinter as tk

from pygments import lex
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name


class Highlighter:
    def __init__(self, master, language=None, *args, **kwargs):
        self.text = master
        self.base = master.base
        self.language = language
        
        if language:
            try:
                self.lexer = get_lexer_by_name(language)
            except:
                self.lexer = None
                return
        else:
            try:
                self.lexer = get_lexer_for_filename(os.path.basename(master.path), inencoding=master.encoding, encoding=master.encoding)
            except:
                self.lexer = None
                return

        self.setup_highlight_tags()

    def setup_highlight_tags(self):
        for token, color in self.base.settings.syntax.items():
            self.text.tag_configure(f"Token.{token}", foreground=color)

    def highlight(self):
        if not self.lexer:
            return
        
        for token, _ in self.base.settings.syntax.items():
            self.text.tag_remove(f"Token.{token}", '1.0', tk.END)
            
        text = self.text.get_all_text()

        # NOTE:  Highlighting only visible area
        # total_lines = int(self.text.index('end-1c').split('.')[0])
        # start_line = int(self.text.yview()[0] * total_lines)
        # first_visible_index = f"{start_line}.0"
        # last_visible_index =f"{self.text.winfo_height()}.end"
        # for token, _ in self.tag_colors.items():
        #     self.text.tag_remove(str(token), first_visible_index, last_visible_index)
        # text = self.text.get(first_visible_index, last_visible_index)

        self.text.mark_set("range_start", '1.0')
        for token, content in lex(text, self.lexer):
            self.text.mark_set("range_end", f"range_start + {len(content)}c")
            self.text.tag_add(str(token), "range_start", "range_end")
            self.text.mark_set("range_start", "range_end")
            
            # DEBUG
            # print(f"{content} is recognized as a <{str(token)}>")
        # print("==================================")
