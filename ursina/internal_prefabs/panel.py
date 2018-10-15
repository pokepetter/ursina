from ursina import *

class Panel(Entity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parent = scene.ui
        self.model = 'quad'
        self.color = Button.color

if __name__ == '__main__':
    app = Ursina()
    p = Panel()
    app.run()
