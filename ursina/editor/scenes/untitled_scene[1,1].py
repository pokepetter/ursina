
class Scene(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Entity(parent=self, position=Vec3(0.8914, 0.3707, -3.1759), rotation=Vec3(0, 40.2606, 0), scale=Vec3(5.452, 5.452, 5.452), model='wireframe_cube', origin=Vec3(0, -0.5, 0), )
