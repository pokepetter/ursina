
def new_project():
    stop()
    resetVertex()
    resetFragment()
    resetGeometry()
    resetPaths()
    get_uniforms()

def open_vertex():
    stop()
    print("Select Vertex Shader File")
    file = tk.filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("vertex shaders files","*.vert"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        print("File selected : "+str(file))
        with open(file, 'r') as f:
            vertexCode.content.delete(1.0, tk.END)
            vertexCode.content.insert(tk.END, f.read())
        vertexCode.path = file
        tabview.set("Vertex")
        vertexCode.focus_force()
        print("Vertex Shader File loaded")
    get_uniforms()

def open_fragment():
    stop()
    print("Select Fragment Shader File")
    file = tk.filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("fragment shaders files","*.frag"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        print("File selected : "+str(file))
        with open(file, 'r') as f:
            fragmentCode.content.delete(1.0, tk.END)
            fragmentCode.content.insert(tk.END, f.read())
        fragmentCode.path = file
        tabview.set("Fragment")
        fragmentCode.focus_force()
        print("Fragment Shader File loaded")
    get_uniforms()
        
def open_geometry():
    stop()
    print("Select Geometry Shader File")
    file = tk.filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("geometry shaders files","*.geom"),("shader files","*.glsl"),("all files","*.*")))
    if file:
        print("File selected : "+str(file))
        with open(file, 'r') as f:
            geometryCode.content.delete(1.0, tk.END)
            geometryCode.content.insert(tk.END, f.read())
        geometryCode.path = file
        tabview.set("Geometry")
        geometryCode.focus_force()
        print("Geometry Shader File loaded")
    get_uniforms()
        
def open_project():
    print("Select Project")
    stop()
    directory = tk.filedialog.askdirectory(initialdir = "./",title = "Select directory")
    if directory:
        resetFragment()
        resetVertex()
        resetGeometry()
        resetPaths()
        print("Directory selected: "+directory)
        files = os.listdir(directory)
        for file in files:
            if file.endswith(".vert"):
                print("Vertex Shader: "+file)
                with open(directory+"/"+file, 'r') as f:
                    vertexCode.content.delete(1.0, tk.END)
                    vertexCode.content.insert(tk.END, f.read())
                vertexCode.path = directory+"/"+file
            elif file.endswith(".frag"):
                print("Fragment Shader: "+file)
                with open(directory+"/"+file, 'r') as f:
                    fragmentCode.content.delete(1.0, tk.END)
                    fragmentCode.content.insert(tk.END, f.read())
                fragmentCode.path = directory+"/"+file
            elif file.endswith(".geom"):
                print("Geometry Shader: "+file)
                with open(directory+"/"+file, 'r') as f:
                    geometryCode.content.delete(1.0, tk.END)
                    geometryCode.content.insert(tk.END, f.read())
                geometryCode.path = directory+"/"+file
        print("Project loaded")
        get_uniforms()
    
       
def save_project(new=False):
    if not new:
        print("Saving Project")
        save_fragment()
        save_vertex()
        save_geometry()
    else:
        print("Select Directory")
        directory = tk.filedialog.askdirectory(initialdir = "./",title = "Select directory")
        print("Directory selected: "+directory)
        if directory:
            print("Saving Project")
            vertexCode.path = directory+"/vertex.vert"
            with open(directory+"/vertex.vert", 'w') as f:
                f.write(vertexCode.content.get(1.0, tk.END).strip())
            fragmentCode.path = directory+"/fragment.frag"
            with open(directory+"/fragment.frag", 'w') as f:
                f.write(fragmentCode.content.get(1.0, tk.END).strip())
            geometryCode.path = directory+"/geometry.geom"
            with open(directory+"/geometry.geom", 'w') as f:
                f.write(geometryCode.content.get(1.0, tk.END).strip())
            print("Project saved")

def save_vertex(new=False):
    if not vertexCode.path or new:
        print("Select Vertex File")
        file = tk.filedialog.asksaveasfile(mode='w', defaultextension=".vert",filetypes = (("vertex shaders files","*.vert"),("shader files","*.glsl"),("all files","*.*")))
        if file:
            print("File selected : "+str(file.name))
            file.write(vertexCode.content.get(1.0, tk.END).strip())
            file.close()
            vertexCode.path = file.name
            print("Vertex saved")
    else:
        print("Saving Vertex")
        with open(vertexCode.path, 'w') as f:
            f.write(vertexCode.content.get(1.0, tk.END).strip())
        print("Vertex saved")
            
def save_fragment(new=False):
    if not fragmentCode.path or new:
        print("Select Fragment File")
        file = tk.filedialog.asksaveasfile(mode='w', defaultextension=".frag",filetypes = (("fragment shaders files","*.frag"),("shader files","*.glsl"),("all files","*.*")))
        if file:
            print("File selected : "+str(file.name))
            file.write(fragmentCode.content.get(1.0, tk.END).strip())
            file.close()
            fragmentCode.path = file.name
            print("Fragment saved")
    else:
        print("Saving Fragment")
        with open(fragmentCode.path, 'w') as f:
            f.write(fragmentCode.content.get(1.0, tk.END).strip())
        print("Fragment saved")
    
def save_geometry(new=False):
    if not geometryCode.path or new:
        print("Select Geometry File")
        file = tk.filedialog.asksaveasfile(mode='w', defaultextension=".geom",filetypes = (("geometry shaders files","*.geom"),("shader files","*.glsl"),("all files","*.*")))
        if file:
            print("File selected : "+str(file.name))
            file.write(geometryCode.content.get(1.0, tk.END).strip())
            file.close()
            geometryCode.path = file.name
            print("Geometry saved")
    else:
        print("Saving Geometry")
        with open(geometryCode.path, 'w') as f:
            f.write(geometryCode.content.get(1.0, tk.END).strip())
        print("Geometry saved")