
class Scene(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Entity(parent=self, position=Vec3(-1.3587,0.032,1.0418), model='cube', origin=Vec3(0,-0.5,0), ignore=True)
        Entity(parent=self, position=Vec3(0.7849,0.034,-1.1488), scale=Vec3(1.9744,1,1), model='cube', origin=Vec3(0,-0.5,0), ignore=True)
        Entity(parent=self, position=Vec3(-2.2072,1.5801,-1.6211), scale=Vec3(2.0645,3.3151,2.0645), model='diamond', origin=Vec3(0,-0.5,0), ignore=True)
        Entity(parent=self, position=Vec3(3.0613,0.1833,-2.9419), scale=Vec3(2.0645,3.3151,2.0645), model='diamond', origin=Vec3(0,-0.5,0), ignore=True)
