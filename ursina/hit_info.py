class HitInfo:
    __slots__ = ['hit', 'entity', 'point', 'world_point', 'distance', 'normal', 'world_normal', 'hits', 'entities']

    def __init__(self, hit=None, entity=None, point=None, world_point=None, distance=9999, normal=None, world_normal=None, hits=None, entities=None):
        self.hit:bool = hit
        self.entity:Entity = entity
        self.point:Vec3 = point
        self.world_point:Vec3 = world_point
        self.distance:float = distance
        self.normal:Vec3 = normal
        self.world_normal:Vec3 = world_normal
        self.hits = hits if hits is not None else []
        self.entities = entities if entities is not None else []

    def __bool__(self):
        return self.hit

    def __repr__(self):
        values_str = ', '.join(f'{slot}={repr(getattr(self, slot))}' for slot in self.__slots__)
        return f'{self.__class__.__name__}({values_str})'