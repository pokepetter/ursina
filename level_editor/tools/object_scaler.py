class ObjectScaler:

    def __init__(self, canvas):
        self.canvas = canvas

    def scale_object(self, obj, scale_factor):
        coords = self.canvas.coords(obj)
        new_coords = [coords[0], coords[1], coords[2] * scale_factor, coords[3] * scale_factor]
        self.canvas.coords(obj, *new_coords)
        print(f"Scaled object {obj} by {scale_factor}")

    def enable(self):
        self.canvas.bind("<Button-3>", self.start_scaling)
        self.canvas.bind("<B3-Motion>", self.perform_scaling)
        self.canvas.bind("<ButtonRelease-3>", self.stop_scaling)
        self.scaling = False

    def start_scaling(self, event):
        self.scaling = True
        self.start_x = event.x
        self.start_y = event.y

    def perform_scaling(self, event):
        if self.scaling:
            scale_factor = (event.x - self.start_x) / 100
            obj = self.canvas.find_closest(self.start_x, self.start_y)
            self.scale_object(obj, scale_factor)

    def stop_scaling(self, event):
        self.scaling = False
