from pandaeditor import *


class Camera(Entity):

    def __init__(self):
        super().__init__()
        self.base = None
        self.cam = None

        self.render = None
        self.ui = None
        # self.aspect_ratio = screen_size[0] / screen_size[1]
        self.aspect_ratio = 1


        self.rotation = (0,0,0)

        self.orthographic_lens = OrthographicLens()
        self.orthographic_lens.setAspectRatio(self.aspect_ratio)

        self.perspective_lens = PerspectiveLens()
        self.perspective_lens.setFocalLength(50)

        self.orthographic = True
        self.fov = 20
        self.clip_plane_near = 0.01
        self.clip_plane_far = 100
        self.lens_node = LensNode('lens_node', self.lens)
        self.lens = self.perspective_lens


    def __setattr__(self, name, value):
        super().__setattr__(name, value)

        # try:
        if name == 'orthographic':
            try:
                print('yay')
                if value == True:
                    self.lens = self.orthographic_lens
                    # self.fov *= .5
                else:
                    self.lens = self.perspective_lens
                    # self.fov *= 2
            except:
                pass

        if name == 'lens':
            self.cam.node().setLens(value)
            self.lens_node = LensNode('lens_node', self.lens)

        if name == 'fov':
            if self.lens == self.orthographic_lens:
                self.lens.setFilmSize(value * self.aspect_ratio, value)
            else:
                self.lens.setFov(value)

        if name == 'near_clip_plane':
            self.lens.setNear(value)
        if name == 'far_clip_plane':
            self.lens.setFar(value)
        # except:
        #     pass # no lens


sys.modules[__name__] = Camera()
