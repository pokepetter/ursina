import sys
from panda3d.core import Vec3
from entity import Entity


class Camera(Entity):

    def __init__(self):
        super().__init__()
        self.cam = None
        self.lens = None
        self.lens_node = None
        self.render = None
        self.ui = None
        self.aspect_ratio = None

        self.fov = 40
        self.clip_plane_near = 0.01
        self.clip_plane_far = 100
        self.rotation = (0,0,0)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

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
