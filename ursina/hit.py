import math


class Hit():
    def __init__(self, **kwargs):
        super().__init__()
        self.hit = None
        self.entity = None
        self.point = None
        self.world_point = None
        self.distance = math.inf
        self.normal = None
        self.world_normal = None

        for key, value in kwargs.items():
            setattr(self, key, value)
