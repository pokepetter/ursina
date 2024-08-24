from ursina import *


class Cylinder(Pipe):
    def __init__(self, resolution=8, radius=.5, height=1, direction=(0,1,0), mode='triangle', **kwargs):
        super().__init__(
            base_shape=Circle(resolution=resolution, radius=.5),
            origin=(0,0),

            path=(
                (0,-(height/2),0), 
                Vec3(direction) * 
                (height/2)
            ),

            thicknesses=((radius*2, radius*2),),
            mode=mode,
            **kwargs
            )


if __name__ == '__main__':
    app = Ursina()
    Entity(model=Cylinder(6), color=color.hsv(60,1,1,.3))
    origin = Entity(model='quad', color=color.orange, scale=(5, .05))
    ed = EditorCamera(rotation_speed = 200, panning_speed=200)
    app.run()
