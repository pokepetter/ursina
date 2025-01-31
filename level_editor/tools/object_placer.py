class ObjectPlacer:

    def __init__(self, canvas):
        self.canvas = canvas
        self.objects = []

    def place_object(self, event):
        obj = self.canvas.create_rectangle(event.x, event.y, event.x + 20, event.y + 20, fill="blue")
        self.objects.append(obj)
        print(f"Placed object at {event.x}, {event.y}")

    def enable(self):
        self.canvas.bind("<Button-1>", self.place_object)
