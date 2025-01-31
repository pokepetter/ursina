from tkinter import Frame, Button

class ToolPanel:

    def __init__(self, parent):
        self.frame = Frame(parent)
        self.create_tools()

    def create_tools(self):
        place_button = Button(self.frame, text="Place Object")
        place_button.pack()

        scale_button = Button(self.frame, text="Scale Object")
        scale_button.pack()

        rotate_button = Button(self.frame, text="Rotate Object")
        rotate_button.pack()

    def pack(self):
        self.frame.pack()
