import tkinter as tk
import builtins

class Console(tk.Text):
    def __init__(self, master, log_file="./data/activity.log", *args, **kwargs):
        super().__init__(master,fg="#c5c8c6",bg="#1d1f21",borderwidth=0,highlightthickness=0,insertbackground="#c5c8c6",font=("Consolas", 12),state=tk.DISABLED, *args, **kwargs)
        self.log_file = log_file
        self.panda_output = ""
        builtins.print = self.console_print
        self.after(100, self.update_console)
        self.clearConsole()
        
    def console_print(self,*args, **kwargs):
        if "log" in kwargs:
            log = kwargs["log"]
            del kwargs["log"]
        else:
            log = True
        if "sep" in kwargs:
            sep = kwargs["sep"]
            del kwargs["sep"]
        else:
            sep = " "
        if "end" in kwargs:
            end = kwargs["end"]
            del kwargs["end"]
        else:
            end = "\n"
        text = sep.join([repr(x) if not isinstance(x,str) else x for x in args])
        for key in kwargs:
            text += f"{key}={repr(kwargs[key])}"+sep
        if kwargs:
            text = text[0:-len(sep)]
        if log and self.log_file:
            with open(self.log_file, "a") as f:
                f.write(text+end)
        self.configure(state=tk.NORMAL)
        self.insert(tk.END, text+end)
        self.configure(state=tk.DISABLED)
        self.see(tk.END)


    def update_console(self):
        with open("./data/panda3d.log", "r") as f:
            new_content = f.read()
        if new_content != self.panda_output:
            self.console_print(new_content[len(self.panda_output):])
            self.panda_output = new_content
        self.after(100, self.update_console)


    def clearConsole(self):
        self.configure(state=tk.NORMAL)
        self.delete(1.0, tk.END)
        self.configure(state=tk.DISABLED)
        with open("./data/panda3d.log", "w") as f:
            f.write("")
            
if __name__ == "__main__":
    root = tk.Tk()
    console = Console(root)
    console.pack()
    console.console_print("Hello World")
    root.mainloop()