import sys
from panda3d.core import Vec3
from entity import Entity


class Camera(Entity):

    def __init__(self):
        super().__init__()
        self.cam = None
        self.lens = None
        self.render = None
        self.ui = None
        self.aspect_ratio = None

        self.fov = 40
        self.clip_plane_near = 0.01
        self.clip_plane_far = 100
        self.rotation = (0,0,0)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        # if name == 'position':
        #     try:
        #         if len(value) % 3 == 0:
        #             new_value = Vec3()
        #             for i in range(0, len(value), 3):
        #                 new_value.addX(value[i])
        #                 new_value.addY(value[i+1])
        #                 new_value.addZ(value[i+2])
        #             value = new_value
        #         self.cam.setPos(value)
        #     except:
        #         pass
                # automatically add position instead of extending the tuple


        #
        #     if name == 'x': self.position = (value, self.position[1], self.position[2])
        #     if name == 'y': self.position = (self.position[0], value, self.position[2])
        #     if name == 'z': self.position = (self.position[0], self.position[1], value)




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
