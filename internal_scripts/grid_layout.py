import sys
sys.path.append("..")
from pandaeditor import *

class GridLayout():

    def __init__(self):
        self.entity = None

        self.origin = (0,0)
        self.overflow = True
        self.spacing = (.005, .005)
        self.max_x = 8
        self.rows = 1
        self.limit = None
        self.width = 0
        self.height = 0


    def update_grid(self):
        grid = chunk_list(self.entity.children, self.max_x)
        self.width = 0
        self.height = 0
        y = 0
        for row in grid:
            if y > 0:
                self.height += max([e.scale_y for e in row]) + self.spacing[1]

            self.width = 0

            for x in range(len(row)):
                if x > 0:
                    self.width += row[x-1].scale_x + self.spacing[0]
                row[x].x = self.width
                row[x].y = -self.height

            y += 1

        # center it
        for c in self.entity.children:
            c.x -= (self.width / 2) + self.entity.children[0].scale_x / 2
            c.y += (self.height / 2) + self.entity.children[0].scale_y / 2


    # def __setattr__(self, name, value):
    #     try:
    #         super().__setattr__(name, value)
    #     except:
    #         pass
    #
    #     # self.update_grid()
    #
    #
    #     # copied from entity
    #     if name == 'origin' and self.model:
    #         new_value = Vec3()
    #
    #         if len(value) % 2 == 0:
    #             for i in range(0, len(value), 2):
    #                 new_value.addX(value[i])
    #                 new_value.addY(value[i+1])
    #             new_value.addZ(self.model.getY())
    #
    #         if len(value) % 3 == 0:
    #             for i in range(0, len(value), 3):
    #                 new_value.addX(value[i])
    #                 new_value.addY(value[i+1])
    #                 new_value.addZ(value[i+2])
    #
    #         self.model.setPos(-new_value[0],
    #                             -new_value[2],
    #                             -new_value[1])
    #         object.__setattr__(self, name, new_value)
