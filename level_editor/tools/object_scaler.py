class ObjectScaler:

    def __init__(self, canvas):
        self.canvas = canvas

    def scale_object(self, obj, scale_factor):
        coords = self.canvas.coords(obj)
        new_coords = [coords[0], coords[1], coords[2] * scale_factor, coords[3] * scale_factor]
        self.canvas.coords(obj, *new_coords)
        print(f"Scaled object {obj} by {scale_factor}")
