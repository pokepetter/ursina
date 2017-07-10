import sys
from panda3d.core import Vec3

class Camera(object):

    def __init__(self):
        self.cam = None
        self.lens = None
        self.render = None

        self.fov = 40
        self.clip_plane_near = 0.01
        self.clip_plane_far = 100

        self.global_position = (0,0,0)
        self.position = (0,0,0)
        self.x, self.y, self.z = 0, 0, 0

        self.rotation = (0,0,0)
        self.rotation_x, self.rotation_y, self.rotation_z = 0, 0, 0

        # self.scale = (1,1,1)
        # self.scale_x, self.scale_y, self.scale_z = 0, 0, 0

        self.forward, self.back = Vec3(0,0,0), Vec3(0,0,0)
        self.right, self.left = Vec3(0,0,0), Vec3(0,0,0)
        self.up, self.down = Vec3(0,0,0), Vec3(0,0,0)


    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)

        if self.cam:
            if name == 'position':
                # automatically add position instead of extending the tuple
                if len(value) % 3 == 0:
                    new_value = Vec3()
                    for i in range(0, len(value), 3):
                        new_value.addX(value[i])
                        new_value.addY(value[i+1])
                        new_value.addZ(value[i+2])
                    value = new_value
                    self.cam.setPos(Vec3(value[0], value[1], value[2]))

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
                self.right =Vec3 (right[0], right[1], right[2])
                self.left = Vec3(-right[0], -right[1], -right[2])

                up = self.render.getRelativeVector(self.cam, (0,0,1))
                self.up = Vec3(up[0], up[1], up[2])
                self.down = Vec3(-up[0], -up[1], -up[2])

            if name == 'rotation_x': self.rotation = (value, self.rotation[1], self.rotation[2])
            if name == 'rotation_y': self.rotation = (self.rotation[0], value, self.rotation[2])
            if name == 'rotation_z': self.rotation = (self.rotation[0], self.rotation[1], value)


        try:
            if name == 'fov':
                self.lens.setFov(value)
            if name == 'near_clip_plane':
                self.lens.setNear(value)
            if name == 'far_clip_plane':
                self.lens.setFar(value)
        except:
            pass # no lens


sys.modules[__name__] = Camera()
