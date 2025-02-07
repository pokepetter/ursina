import tkinter as tk
import tkinter.colorchooser as colorchooser
import customtkinter
from ursina import Texture,Vec2,Vec3,Vec4

class Uniform(customtkinter.CTkFrame):
    def __init__(self, master,name,type, camera, default_value=None, params=None):
        super().__init__(master)
        self.master = master
        self.name = name
        self.type = type
        self._default_value = default_value
        self._params = params
        self._cam = camera
        self.create_widgets()
        if self.get() != None:
            self.update_shader()
        

    def create_widgets(self):
        self.create_label()
        self.create_entry()

    def create_label(self):
        self.uniform_label = customtkinter.CTkLabel(self, text=self.name + " (" + self.type + ")")
        self.uniform_label.pack(side="left",padx=20)

    def create_entry(self):
        pass

    def get(self):
        pass

    def update_shader(self,event=None):
        print(f"Updating {self.name} to {self.get()}")
        self._cam.set_shader_input(self.name, self.get())

class UniformInt(Uniform):
    def create_entry(self):
        self.uniform_entry = customtkinter.CTkSlider(self, from_=0, to=100, command=self.update_shader)
        if self._params:
            print(params=(self._params[0],self._params[1]))
            self.uniform_entry.configure(from_=self._params[0], to=self._params[1])
        if self._default_value:
            print(default_value=self._default_value)
            self.uniform_entry.set(self._default_value)
        self.uniform_entry.pack(side="right")

    def get(self):
        return int(self.uniform_entry.get())

class UniformFloat(Uniform):
    def create_entry(self):
        self.uniform_entry = customtkinter.CTkEntry(self)
        self.uniform_entry.bind("<Return>", self.update_shader)
        self.uniform_entry.bind("<FocusOut>", self.update_shader)
        if self._default_value:
            self._default_value = float(self._default_value)
            self.uniform_entry.insert(tk.END,self._default_value)
        else:
            self.uniform_entry.insert(tk.END,"0")
        self.uniform_entry.pack(side="right")
        self.update_shader()
        
    def get(self):
        if self.uniform_entry.get():
            return float(self.uniform_entry.get())
        return 0

class UniformBool(Uniform):
    def create_entry(self):
        self.uniform_entry = customtkinter.CTkSwitch(self, text="On/Off", command=self.update_shader)
        if self._default_value:
            if self._default_value:
                self.uniform_entry.select()
            else:
                self.uniform_entry.deselect()
        self.uniform_entry.pack(side="right")

    def get(self):
        return self.uniform_entry.get()

class UniformImage(Uniform):
    def create_entry(self):
        self._image = None;
        self.uniform_entry = customtkinter.CTkButton(self, text="Choose Image", command=self.image_picker)
        self.uniform_entry.pack(side="right")
    
    def image_picker(self):
        new_image = tk.filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("images files","*.jpg *.png *.jpeg"),("all files","*.*")))
        if new_image:
            self._image = Texture(new_image)
            self.update_shader()
    
    def get(self):
        return self._image
    
class UniformColor3(Uniform):
    def create_entry(self):
        self._color = None
        self.uniform_entry = customtkinter.CTkButton(self, text="Choose Color", command=self.color_picker)
        self.uniform_entry.pack(side="right")
        if self._default_value:
            self._color = self._default_value
            
        else:
            self._color = Vec3(1)
    
    def color_picker(self):
        new_color = colorchooser.askcolor()
        if new_color != (None,None):
            self._color = Vec3(*new_color[0])/255
            self.update_shader()
    
    def get(self):
        return self._color

class UniformColor4(Uniform):
    def create_entry(self):
        self._color = None
        self.uniform_entry = customtkinter.CTkButton(self, text="Choose Color", command=self.color_picker)
        self.alpha_entry = customtkinter.CTkSlider(self, from_=0, to=1, command=self.set_alpha)
        self.alpha_entry.pack(side="right")
        self.alpha_label = customtkinter.CTkLabel(self, text="Alpha")
        self.alpha_label.pack(side="right")
        self.uniform_entry.pack(side="right")
        if self._default_value or self._default_value == 0:
            self._color = Vec4(self._default_value)
            self._alpha = self._color.w
            self.alpha_entry.set(self._alpha)
        else:
            self._color = Vec4(1)
            self._alpha = 1
            self.alpha_entry.set(1)
    
    def color_picker(self):
        new_color = colorchooser.askcolor()
        if new_color != (None,None):
            self._color = Vec4(Vec3(*new_color[0])/255,self._alpha)
            self.update_shader()
    
    def set_alpha(self,alpha):
        self._alpha = alpha
        self._color[3] = alpha
        self.update_shader()
        
    def get(self):
        return self._color

class UniformVec2(Uniform):
    
    def create_entry(self):
        self.entry1 = customtkinter.CTkEntry(self)
        self.entry2 = customtkinter.CTkEntry(self)
        if self._default_value:
            self._default_value = Vec2(self._default_value)
            self.entry1.insert(tk.END,self._default_value[0])
            self.entry2.insert(tk.END,self._default_value[1])
        else:
            self.entry1.insert(tk.END,"0")
            self.entry2.insert(tk.END,"0")
        self.entry1.pack(side="right")
        self.entry2.pack(side="right")
        self.entry1.bind("<Return>", self.update_shader)
        self.entry1.bind("<FocusOut>", self.update_shader)
        self.entry2.bind("<Return>", self.update_shader)
        self.entry2.bind("<FocusOut>", self.update_shader)
        self.update_shader()
        
    def get(self):
        if self.entry1.get() and self.entry2.get():
            return Vec2(float(self.entry1.get()),float(self.entry2.get()))
        return Vec2(0,0)