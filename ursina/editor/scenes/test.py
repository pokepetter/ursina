
class Scene(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Entity(parent=self, position=Vec3(-1.0334,0,3.0372), model='cube', color=color.hsv(0,1,1))
        # self.ground = Entity(parent=self, scale=Vec3(16,16,16), model='plane', color=color.hsv(120,1,1))
        Entity(parent=self, position=Vec3(1.8813,0,2.3903), scale=Vec3(1,2,1), model='cube', origin=Vec3(0,-0.5,0), color=color.hsv(30,1,1))
        Entity(parent=self, position=Vec3(-2.1674,0.064,2.3704), model='cube', color=color.hsv(330,1,1))
        # Entity(parent=self.ground, position=Vec3(0.501,0.064,2.7009), model='cube', color=color.hsv(330,1,1))
