from ursina import *


class LoadingWheel(Entity):
    def __init__(self):
        super().__init__()
        self.parent = camera.ui
        self.point = Entity(
            parent=self,
            model=Circle(24, mode='point', thickness=3),
            color=color.light_gray,
            y=.75,
            scale=2
            )
        self.point2 = Entity(
            parent=self,
            model=Circle(12, mode='point', thickness=3),
            color=color.light_gray,
            y=.75,
            scale=1
            )
        self.scale = .025
        self.text_entity = Text(
            world_parent = self,
            text = '  loading...',
            origin = (0,1.5),
            color = color.light_gray,
            )
        self.y = -.25


    def update(self):
        self.point.rotation_y += 5
        self.point2.rotation_y += 3

if __name__ == '__main__':
    app = Ursina()
    window.color = color.black
    LoadingWheel()
    app.run()
