from ursina import *
import math


class PositionLimiter():
    def __init__(self, min_x=-inf, max_x=inf, min_y=-inf, max_y=inf, min_z=-inf, max_z=inf):
        super().__init__()
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.min_z = min_z
        self.max_z = max_z

    def update(self):
        self.entity.x = clamp(self.entity.x, self.min_x, self.max_x)
        self.entity.y = clamp(self.entity.y, self.min_y, self.max_y)
        self.entity.z = clamp(self.entity.z, self.min_z, self.max_z)
