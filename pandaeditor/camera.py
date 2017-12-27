import sys
from pandaeditor.entity import Entity
from panda3d.core import PerspectiveLens, OrthographicLens, LensNode, NodePath
from panda3d.core import Camera as PandaCamera
from pandaeditor import application
from pandaeditor import scene
from pandaeditor import window
from pandaeditor import color

class Camera(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'camera'
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
        self.perspective_lens.set_aspect_ratio(self.aspect_ratio)
        self.perspective_lens.set_focal_length(50)
        self.perspective_lens_node = LensNode('perspective_lens_node', self.perspective_lens)
        self.fov = 40
        self.clip_plane_near = 0.01
        self.clip_plane_far = 100

        self.lens = self.perspective_lens
        self.lens_node = self.perspective_lens_node
        application.base.cam.node().set_lens(self.perspective_lens)

        win.setClearColor(color.dark_gray)
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

        ui = Entity()
        ui.name = 'ui'
        ui.is_editor = True
        ui.parent = self.ui_camera
        ui.model = 'quad'
        ui.scale = (self.ui_size * .5, self.ui_size * .5)
        # ui.color = color.white33
        if ui.model:
            ui.model.hide()
        scene.ui = ui
        self.ui = ui


    def __setattr__(self, name, value):

        if name == 'fov':
            value = max(1, value)
            try:
                self.perspective_lens.set_fov(value)
                application.base.cam.node().set_lens(self.perspective_lens)
            except:
                pass # no lens


        elif name == 'near_clip_plane':
            self.lens.set_near(value)
        elif name == 'far_clip_plane':
            self.lens.set_far(value)

        if name == 'rect':
            self.ui_display_region = self.display_region = win.make_display_region(0, 1, 0, 1)

        super().__setattr__(name, value)

    @property
    def aspect_ratio(self):
        try:
            return window.size[0] / window.size[1]
        except:
            return 16 / 9

sys.modules[__name__] = Camera()
