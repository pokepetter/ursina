from tkinter import Tk, Menu, Frame, Button

class EditorWindow:

    def __init__(self):
        self.root = Tk()
        self.root.title("Level Editor")
        self.create_menu()
        self.create_layout()

    def create_menu(self):
        menu_bar = Menu(self.root)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Level")
        file_menu.add_command(label="Load Level")
        file_menu.add_command(label="Save Level")
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

    def create_layout(self):
        self.frame = Frame(self.root)
        self.frame.pack()

        self.place_button = Button(self.frame, text="Place Object")
        self.place_button.pack()

        self.scale_button = Button(self.frame, text="Scale Object")
        self.scale_button.pack()

        self.rotate_button = Button(self.frame, text="Rotate Object")
        self.rotate_button.pack()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    window = EditorWindow()
    window.run()
