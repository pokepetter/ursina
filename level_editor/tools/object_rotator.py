import math

class ObjectRotator:

    def __init__(self, canvas):
        self.canvas = canvas

    def rotate_object(self, obj, angle):
        coords = self.canvas.coords(obj)
        center_x = (coords[0] + coords[2]) / 2
        center_y = (coords[1] + coords[3]) / 2
        new_coords = []

        for i in range(0, len(coords), 2):
            x, y = coords[i], coords[i+1]
            new_x = center_x + (x - center_x) * math.cos(angle) - (y - center_y) * math.sin(angle)
            new_y = center_y + (x - center_x) * math.sin(angle) + (y - center_y) * math.cos(angle)
            new_coords.extend([new_x, new_y])

        self.canvas.coords(obj, *new_coords)
        print(f"Rotated object {obj} by {angle} degrees")
