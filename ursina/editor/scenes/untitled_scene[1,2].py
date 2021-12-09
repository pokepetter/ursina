
class Scene(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Entity(parent=self, position=Vec3(0.4138,0.032,-2.857), model='cube', origin=Vec3(0,-0.5,0), ignore=True)
        Entity(parent=self, position=Vec3(-3.6067,0.032,-4.2204), model='cube', origin=Vec3(0,-0.5,0), ignore=True)
        Entity(parent=self, position=Vec3(-7.2283,0.032,-2.2602), model='cube', origin=Vec3(0,-0.5,0), ignore=True)
