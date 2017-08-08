from pandaeditor import *


class Camera(Entity):

    def __init__(self):
        super().__init__()
        self.base = None
        self.cam = None
        self.lens = None

        self.render = None
        self.ui = None
        # self.aspect_ratio = screen_size[0] / screen_size[1]
        self.aspect_ratio = 1


        self.rotation = (0,0,0)

        self.orthographic_lens = OrthographicLens()
        self.orthographic_lens.setFilmSize(20)
        self.orthographic_lens.setAspectRatio(self.aspect_ratio)

        self.perspective_lens = PerspectiveLens()
        self.perspective_lens.setFocalLength(50)

        self.orthographic = True
        self.fov = 40
        self.clip_plane_near = 0.01
        self.clip_plane_far = 100
        self.lens_node = LensNode('lens_node', self.lens)


    def __setattr__(self, name, value):
        super().__setattr__(name, value)

        try:
            if name == 'orthographic':
                if value == True:
                    self.lens = self.orthographic_lens
                else:
                    self.lens = self.perspective_lens

            if name == 'lens':
                self.cam.node().setLens(value)

            if name == 'fov':
                if value == 0 or value == math.infinity and self.lens == perspective_lens:
                    self.lens = orthographic_lens
                self.lens.setFov(value)

            if name == 'near_clip_plane':
                self.lens.setNear(value)
            if name == 'far_clip_plane':
                self.lens.setFar(value)
        except:
            pass # no lens


sys.modules[__name__] = Camera()
