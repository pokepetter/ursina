import sys
from ursina.entity import Entity
from panda3d.core import PerspectiveLens, OrthographicLens, LensNode, NodePath
from panda3d.core import Camera as PandaCamera
from ursina import application
from ursina import scene
from ursina import window
from ursina import color


class Camera(Entity):

    def __init__(self):
        super().__init__()
        self.parent = scene
        self.name = 'camera'
        self.eternal = True
        self.is_editor = True

        self.cam = None
        self.render = None
        self.ui_size = 40
        self.ui_lens_node = None
        self.ui = None
        self.fov = 40


    def set_up(self):
        print('setting up')
        win = base.camNode.get_display_region(0).get_window()
        self.display_region = win.make_display_region(0, 1, 0, 1)


        self.perspective_lens = PerspectiveLens()
        self.lens = self.perspective_lens
        self.perspective_lens.set_aspect_ratio(window.aspect_ratio)
        self.perspective_lens.set_focal_length(50)
        self.perspective_lens_node = LensNode('perspective_lens_node', self.perspective_lens)
        self.lens_node = self.perspective_lens_node

        self.orthographic_lens = OrthographicLens()
        self.orthographic_lens.set_film_size(self.fov * window.aspect_ratio, self.fov)
        self.orthographic_lens_node = LensNode('orthographic_lens_node', self.orthographic_lens)

        application.base.cam.node().set_lens(self.lens)
        self.orthographic = False

        self.fov = 40
        self.clip_plane_near = 0.01
        self.clip_plane_far = 100

        # win.setClearColor(color.dark_gray)
        self.ui_display_region = win.make_display_region()
        self.ui_display_region.set_sort(20)

        self.ui_camera = NodePath(PandaCamera('ui_camera'))
        self.ui_lens = OrthographicLens()
        self.ui_lens.set_film_size(self.ui_size * .5 * self.aspect_ratio, self.ui_size * .5)
        self.ui_lens.set_near_far(-1000, 1000)
        self.ui_camera.node().set_lens(self.ui_lens)
        self.ui_lens_node = LensNode('ui_lens_node', self.ui_lens)

        self.ui_render = NodePath('ui_render')
        self.ui_render.set_depth_test(0)
        self.ui_render.set_depth_write(0)
        self.ui_camera.reparent_to(self.ui_render)
        self.ui_display_region.set_camera(self.ui_camera)
        scene.ui_camera = self.ui_camera
        # ui_camera.hide()

        self.ui = Entity()
        self.ui.eternal = True
        self.ui.name = 'ui'
        self.ui.is_editor = True
        self.ui.parent = self.ui_camera
        self.original_ui_scale = (self.ui_size * .5, self.ui_size * .5)
        self.ui.scale = self.original_ui_scale
        # self.ui.model = 'quad'
        scene.ui = self.ui


    @property
    def orthographic(self):
        return self._orthographic

    @orthographic.setter
    def orthographic(self, value):
        self._orthographic = value
        if value == True:
            self.lens = self.orthographic_lens
            self.lens_node = self.orthographic_lens_node
            application.base.cam.node().set_lens(self.orthographic_lens)
        else:
            self.lens = self.perspective_lens
            self.lens_node = self.perspective_lens_node
            application.base.cam.node().set_lens(self.perspective_lens)

        self.fov = self.fov



    def __setattr__(self, name, value):

        if name == 'fov':
            value = max(1, value)
            if hasattr(self, 'perspective_lens'):
                self.perspective_lens.set_fov(value)
                # print('from:', self.perspective_lens_node.getPos())
                # self.perspective_lens_node.set_y(self.perspective_lens_node.get_y() + 10)
                # print('to:', self.perspective_lens_node.get_y())
                # self.z = value
                application.base.cam.node().set_lens(self.perspective_lens)
            elif hasattr(self, 'orthographic_lens'):
                self.orthographic_lens.set_film_size(value * self.aspect_ratio, value)
                application.base.cam.node().set_lens(self.orthographic_lens)
                super().__setattr__(name, value)
                return

        elif name == 'near_clip_plane':
            self.lens.set_near(value)
        elif name == 'far_clip_plane':
            self.lens.set_far(value)

        if name == 'rect':
            self.ui_display_region = self.display_region = win.make_display_region(0, 1, 0, 1)

        super().__setattr__(name, value)

    @property
    def aspect_ratio(self):
        # try:
        # return window.size[0] / window.size[1]
        return self.lens.get_aspect_ratio()
        # except:
        #     return 16 / 9

    @aspect_ratio.setter
    def aspect_ratio(self, value):
        print('setting camera aspect ratio')
        self.perspective_lens = PerspectiveLens()
        self.perspective_lens.set_aspect_ratio(value)
        application.base.cam.node().set_lens(self.perspective_lens)
        # self.perspective_lens.set_aspect_ratio(value)
        # self.orthographic_lens = OrthographicLens()
        # self.orthographic_lens.set_film_size(self.fov * value, self.fov)

sys.modules[__name__] = Camera()


if __name__ == '__main__':
    from ursina.main import Ursina
    app = Ursina()
    # app.load_editor()
    scene.camera.orthographic = True
    e = Entity()
    e.model = 'quad'
    e.color = color.random_color()
    e.position = (-2, 0, 10)

    e = Entity()
    e.model = 'quad'
    e.color = color.random_color()
    e.position = (2, 0, 10)

    e = Entity()
    e.model = 'quad'
    e.color = color.random_color()
    e.position = (0, 0, 40)
    # from ursina import *
    # Button(text='test button')
    app.run()
