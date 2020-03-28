
class Scene(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        RedCube(parent=self, position=Vec3(0,0,4), model='cube', color=color.hsv(0,1,1))
        GreenPlane(parent=self, scale=Vec3(16,16,16), model='plane', color=color.hsv(120,1,1))
        OrangeCube(parent=self, position=Vec3(1,0,0), scale=Vec3(1,2,1), model='cube', origin=Vec3(0,-0.5,0), color=color.hsv(30,1,1))
        PinkCube(parent=self, position=Vec3(-1.2747,0.064,-3.15), model='cube', color=color.hsv(330,1,1))
        PinkCube(parent=self, position=Vec3(1.7366,0.064,-2.5117), model='cube', color=color.hsv(330,1,1))
