from pandaeditor import *


class Camera(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'camera'
        self.is_editor = True
        self.cam = None

        self.render = None
        self.ui = None
        self.ui_lens_node = None
        self.fov = 40
        self.rotation = (0,0,0)


    def set_up(self):
        print('setting up')
        self.perspective_lens = PerspectiveLens()
        self.perspective_lens.setAspectRatio(self.aspect_ratio)
        self.perspective_lens.setFocalLength(50)
        self.perspective_lens_node = LensNode('perspective_lens_node', self.perspective_lens)
        self.fov = 40
        self.clip_plane_near = 0.01
        self.clip_plane_far = 100

        self.lens = self.perspective_lens
        self.lens_node = self.perspective_lens_node
        application.base.cam.node().setLens(self.perspective_lens)


    def __setattr__(self, name, value):

        if name == 'fov':
            value = max(1, value)
            try:
                self.perspective_lens.setFov(value)
                application.base.cam.node().setLens(self.perspective_lens)
            except:
                pass # no lens


        elif name == 'near_clip_plane':
            self.lens.setNear(value)
        elif name == 'far_clip_plane':
            self.lens.setFar(value)

        super().__setattr__(name, value)


sys.modules[__name__] = Camera()
