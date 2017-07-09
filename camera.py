import sys
from panda3d.core import Vec3

class Camera():

    def __init__(self):
        self.cam = None
        self.render = None
        self.position = (0,0,0)
        self.x, self.y, self.z = 0, 0, 0

        self.rotation = (0,0,0)
        self.rotation_x, self.rotation_y, self.rotation_z = 0, 0, 0

        # self.scale = (1,1,1)
        # self.scale_x, self.scale_y, self.scale_z = 0, 0, 0

        self.forward, self.back = (0,0,0), (0,0,0)
        self.right, self.left = (0,0,0), (0,0,0)
        self.up, self.down = (0,0,0), (0,0,0)


    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if self.cam:
            if name == 'position':
                # automatically add position instead of extending the tuple
                if len(value) % 3 == 0 and len(value) > 3:
                    new_value = Vec3()
                    for i in range(0, len(value), 3):
                        new_value.addX(value[i])
                        new_value.addY(value[i+1])
                        new_value.addZ(value[i+2])
                    self.position = new_value
                self.cam.setPos(value)
            if name == 'x': self.position = (value, self.position[1], self.position[2])
            if name == 'y': self.position = (self.position[0], value, self.position[2])
            if name == 'z': self.position = (self.position[0], self.position[1], value)

            if name == 'rotation':
                # convert value from hpr to axis
                value = (value[2] , value[0], value[1])
                self.cam.setHpr(value)

                forward = self.render.getRelativeVector(self.cam, (0,1,0))
                self.forward = (forward[0], forward[1], forward[2])
                self.back = (-forward[0], -forward[1], -forward[2])

                right = self.render.getRelativeVector(self.cam, (1,0,0))
                self.right = (right[0], right[1], right[2])
                self.left = (-right[0], -right[1], -right[2])

                up = self.render.getRelativeVector(self.cam, (0,0,1))
                self.up = (up[0], up[1], up[2])
                self.down = (-up[0], -up[1], -up[2])

            if name == 'rotation_x': self.rotation = (value, self.rotation[1], self.rotation[2])
            if name == 'rotation_y': self.rotation = (self.rotation[0], value, self.rotation[2])
            if name == 'rotation_z': self.rotation = (self.rotation[0], self.rotation[1], value)



sys.modules[__name__] = Camera()
