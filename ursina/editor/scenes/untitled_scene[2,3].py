class Scene(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Entity(parent=self, position=Vec3(2.1786,0.033,6.256), model='cube', origin=Vec3(0,-0.5,0), ignore=True)
        Entity(parent=self, position=Vec3(-0.9924,0.032,5.2352), model='cube', origin=Vec3(0,-0.5,0), ignore=True)
        Entity(parent=self, position=Vec3(1.2385,0.032,6.6089), model='cube', origin=Vec3(0,-0.5,0), ignore=True)
        Entity(parent=self, position=Vec3(0.1564,0.032,6.6415), model='cube', origin=Vec3(0,-0.5,0), ignore=True)
        Entity(parent=self, position=Vec3(-1.9521,0.032,6.7786), model='cube', origin=Vec3(0,-0.5,0), ignore=True)
        Entity(parent=self, position=Vec3(3.7492,0.032,7.5643), model='cube', origin=Vec3(0,-0.5,0), ignore=True)
