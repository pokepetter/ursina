import math


class HitInfo:
    __slots__ = ['hit', 'entity', 'point', 'world_point', 'distance', 'normal', 'world_normal', 'hits', 'entities']


    def __init__(self, **kwargs):

        self.hit = None
        self.entity = None
        self.point = None
        self.world_point = None
        self.distance = math.inf
        self.normal = None
        self.world_normal = None
        self.hits = []
        self.entities = []

        for key, value in kwargs.items():
            setattr(self, key, value)


    def __bool__(self):
        return self.hit
