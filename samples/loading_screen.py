from ursina import *

# class LoadingWheel(Entity):
#     def __init__(self):
#         super().__init__()
#         self.parent = camera.ui
#         self.point = Entity(parent=self, model='sphere', color=color.light_gray, y=.75, scale=.5)
#         self.scale = .025
#         self.text_entity = Text(
#             'loading...',
#             origin = (0,2.5),
#             color = color.light_gray,
#             )
#
#     def update(self):
#         self.rotation_z += 5
#         particle = duplicate(self.point)
#         particle.world_parent = self.parent
#         particle.color = color.color(0,0,1,.1)
#         # particle.color = color.light_gray
#         # particle.fade_out(duration=.3)
#         # particle.position = self.point
#         destroy(particle, delay=.5)

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
