from tkinter import Tk, Menu

class EditorWindow:

    def __init__(self):
        self.root = Tk()
        self.root.title("Level Editor")
        self.create_menu()

    def create_menu(self):
        menu_bar = Menu(self.root)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Level")
        file_menu.add_command(label="Load Level")
        file_menu.add_command(label="Save Level")
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    window = EditorWindow()
    window.run()
