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

        self._cam = None
        self._render = None
        self.ui_size = 40
        self._ui_lens_node = None
        self.ui = None
        self.fov = 40
        self.orthographic = False


    def set_up(self):
        self.display_region = base.camNode.get_display_region(0)
        win = self.display_region.get_window()

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
        self.clip_plane_near = 0.0001
        self.clip_plane_far = 10000

        self.ui_display_region = win.make_display_region()
        self.ui_display_region.set_sort(20)

        self.ui_camera = NodePath(PandaCamera('ui_camera'))
        self.ui_lens = OrthographicLens()
        self.ui_lens.set_film_size(self.ui_size * .5 * self.aspect_ratio, self.ui_size * .5)
        self.ui_lens.set_near_far(-1000, 1000)
        self.ui_camera.node().set_lens(self.ui_lens)
        self._ui_lens_node = LensNode('_ui_lens_node', self.ui_lens)

        self.ui_render = NodePath('ui_render')
        self.ui_render.set_depth_test(0)
        self.ui_render.set_depth_write(0)
        self.ui_camera.reparent_to(self.ui_render)
        self.ui_display_region.set_camera(self.ui_camera)
        scene.ui_camera = self.ui_camera
        # ui_camera.hide()

        # self.black_bars_display_region = win.make_display_region()
        # self.black_bars_display_region.set_sort(-100)

        self.ui = Entity()
        self.ui.eternal = True
        self.ui.name = 'ui'
        self.ui.parent = self.ui_camera
        self.ui.scale = (self.ui_size*.5, self.ui_size*.5)
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
            application.base._cam.node().set_lens(self.orthographic_lens)
        else:
            self.lens = self.perspective_lens
            self.lens_node = self.perspective_lens_node
            application.base._cam.node().set_lens(self.perspective_lens)

        self.fov = self.fov


    @property
    def fov(self):
        return self._fov

    @fov.setter
    def fov(self, value):
        value = max(1, value)
        self._fov = value
        if not self.orthographic and hasattr(self, 'perspective_lens'):
            self.perspective_lens.set_fov(value)
            application.base._cam.node().set_lens(self.perspective_lens)

        elif self.orthographic and hasattr(self, 'orthographic_lens'):
            self.orthographic_lens.set_film_size(value * self.aspect_ratio, value)
            application.base._cam.node().set_lens(self.orthographic_lens)

    @property
    def clip_plane_near(self):
        return self.lens.getNear()

    @clip_plane_near.setter
    def near_clip_plane(self, value):
        self.lens.set_near(value)

    @property
    def clip_plane_far(self):
        return self.lens.getFar()

    @clip_plane_far.setter
    def clip_plane_far(self, value):
        self.lens.set_far(value)

    @property
    def aspect_ratio(self):
        return self.perspective_lens.get_aspect_ratio()

    @aspect_ratio.setter
    def aspect_ratio(self, value):
        self.perspective_lens = PerspectiveLens()
        self.perspective_lens.set_aspect_ratio(value)
        application.base._cam.node().set_lens(self.perspective_lens)

        self.ui_lens.set_film_size(self.ui_size * .5 * value, self.ui_size * .5)
        self.ui_camera.node().set_lens(self.ui_lens)
        self._ui_lens_node = LensNode('_ui_lens_node', self.ui_lens)
        print('setting camera aspect ratio')
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
