class HitInfo:
    __slots__ = ['hit', 'entity', 'point', 'world_point', 'distance', 'normal', 'world_normal', 'hits', 'entities']

    def __init__(self, **kwargs):
        self.hit:bool = None
        self.entity:Entity = None
        self.point:Vec3 = None
        self.world_point:Vec3 = None
        self.distance:float = 9999
        self.normal:Vec3 = None
        self.world_normal:Vec3 = None
        self.hits = []
        self.entities = []

        for key, value in kwargs.items():
            setattr(self, key, value)


    def __bool__(self):
        return self.hit
