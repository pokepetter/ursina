from pandaeditor import *


class Camera(Entity):

    def __init__(self):
        super().__init__()
        self.base = None
        self.cam = None

        self.render = None
        self.ui = None


    def set_up(self):
        print('setting up')

        self.orthographic_lens = OrthographicLens()
        self.orthographic_lens.setAspectRatio(self.aspect_ratio)

        self.perspective_lens = PerspectiveLens()
        self.perspective_lens.setFocalLength(50)

        self.orthographic_lens_node = LensNode('orthographic_lens_node', self.orthographic_lens)
        self.perspective_lens_node = LensNode('perspective_lens_node', self.perspective_lens)

        self.orthographic = True
        self.fov = 20
        self.clip_plane_near = 0.01
        self.clip_plane_far = 100

        self.base.cam.node().setLens(self.lens)


    def __setattr__(self, name, value):

        if name == 'orthographic':
            print('ortho', value)
            # try:
            if value == True:
                self.lens = self.orthographic_lens
                self.lens_node = self.orthographic_lens_node
                self.base.cam.node().setLens(self.orthographic_lens)
                # self.fov = self.fov / 2
            else:
                self.lens = self.perspective_lens
                self.lens_node = self.perspective_lens_node
                self.base.cam.node().setLens(self.perspective_lens)
                self.fov *= 2

        if name == 'fov':
            if self.lens == self.orthographic_lens:
                self.lens.setFilmSize(value * self.aspect_ratio, value)
            else:
                self.lens.setFov(value)
        #
        # elif name == 'near_clip_plane':
        #     self.lens.setNear(value)
        #     return
        # elif name == 'far_clip_plane':
        #     self.lens.setFar(value)
        super().__setattr__(name, value)


sys.modules[__name__] = Camera()
