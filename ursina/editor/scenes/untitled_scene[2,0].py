
class Scene(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        Entity(parent=self, model='cube', position=Vec3(0.0,0.0,4.0), color=color.hsv(0.0,1.0,1.0))
        Entity(parent=self, model='plane', position=Vec3(0.0,0.0,0.0), color=color.hsv(120.0,1.0,1.0))
        Entity(parent=self, model='cube', position=Vec3(-1.2448334693908691,0.0,1.6809353828430176), color=color.hsv(30.0,1.0,1.0))
