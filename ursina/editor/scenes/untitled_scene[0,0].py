class Scene(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Entity(parent=self, position=Vec3(-1.3587, 0.032, 1.0418), model='cube', origin=Vec3(0, -0.5, 0), )
        Entity(parent=self, position=Vec3(0.7849, 0.034, -1.1488), scale=Vec3(1.9744, 1, 1), model='cube', origin=Vec3(0, -0.5, 0), )
        Entity(parent=self, position=Vec3(-2.2072, 1.5801, -1.6211), scale=Vec3(2.0645, 3.3151, 2.0645), model='diamond', origin=Vec3(0, -0.5, 0), )
        Entity(parent=self, position=Vec3(3.0613, 0.1833, -2.9419), scale=Vec3(2.0645, 3.3151, 2.0645), model='diamond', origin=Vec3(0, -0.5, 0), )
        PokeShape(parent=self, position=Vec3(0.686502, 0.00099954, -2.04429), texture='grass', points=[Vec3(-7.79579, 0, -4.98429), Vec3(4.0883, 0, -3.73695), Vec3(5.73138, 0, 6.07817), Vec3(-3.13966, 0, 6.57585)], )
