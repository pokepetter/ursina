from ursina import *
from ursina.models.procedural.quad import Quad
from ursina.prefabs.button import Button


class Panel(Entity):

    def __init__(self, **kwargs):
        super().__init__()
        self.parent = camera.ui
        self.model = Quad()
        self.color = Button.default_color

        for key, value in kwargs.items():
            setattr(self, key, value)

if __name__ == '__main__':
    app = Ursina()
    p = Panel()
    app.run()
