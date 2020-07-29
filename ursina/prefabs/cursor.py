from ursina import *


class Cursor(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.parent = camera.ui
        self.texture = 'cursor'
        self.model = 'quad'
        self.color = color.light_gray
        # self.origin = (-.49, .49)
        self.scale *= .05
        self.render_queue = 1

        for key, value in kwargs.items():
            setattr(self, key, value)


    def update(self):
        self.position = Vec3(mouse.x, mouse.y, -100)




if __name__ == '__main__':
    app = Ursina()
    Button('button').fit_to_text()
    Panel()
    camera.orthographic = True
    camera.fov = 100
    e = Entity(model='cube')
    mouse._mouse_watcher.setGeometry(e.model.node())
    # cursor =  Cursor(
    #     texture=None,
    #     model=Mesh(
    #         vertices=[(-.5,0,0), (.5,0,0), (0,-.5,0), (0,.5,0)],
    #         triangles=[(0,1), (2,3)],
    #         mode='line',
    #         thickness=2,
    #         ),
    #     scale=.02
    #     )
    mouse.visible = False
    app.run()
