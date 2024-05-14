from ursina import entity
from ursina.entity import Entity
from panda3d.core import PerspectiveLens, OrthographicLens, LensNode, NodePath
from panda3d.core import Camera as PandaCamera
from panda3d.core import Texture as PandaTexture
from direct.filter.FilterManager import FilterManager
from ursina import application
from ursina.scene import instance as scene
from ursina.window import instance as window
from ursina import color
from ursina.texture import Texture
from ursina.shader import Shader
from ursina.string_utilities import print_info

from ursina.scripts.property_generator import generate_properties_for_class
@generate_properties_for_class()
class Camera(Entity):
    def __init__(self):
        original_warn_if_ursina_not_instantiated = entity._warn_if_ursina_not_instantiated
        entity._warn_if_ursina_not_instantiated = False
        super().__init__()
        entity._warn_if_ursina_not_instantiated = original_warn_if_ursina_not_instantiated

        self.parent = scene
        self.name = 'camera'
        self.eternal = True

        self._cam = None
        self._render = None
        self.ui_size = 40

        self._ui_lens_node = None
        self.perspective_lens_node = None
        self.orthographic_lens_node = None
        self.ui = Entity(eternal=True, name='ui', scale=(self.ui_size*.5, self.ui_size*.5), add_to_scene_entities=False)
        self.overlay = Entity(parent=self.ui, model='quad', scale=99, color=color.clear, eternal=True, z=-99, add_to_scene_entities=False)
        # self.ready = False
        # self._orthographic = False
        # self._fov = 40   # horizontal fov


    def set_up(self):
        self.display_region = application.base.camNode.get_display_region(0)
        win = self.display_region.get_window()

        self.perspective_lens = PerspectiveLens()
        self.perspective_lens = application.base.camLens # use panda3d's default for automatic aspect ratio on window resize
        self.lens = self.perspective_lens
        self.perspective_lens.set_aspect_ratio(window.aspect_ratio)
        self.perspective_lens_node = LensNode('perspective_lens_node', self.perspective_lens)
        self.lens_node = self.perspective_lens_node

        self.orthographic_lens = OrthographicLens()
        self.orthographic_lens.set_film_size(self.fov * window.aspect_ratio, self.fov)
        self.orthographic_lens_node = LensNode('orthographic_lens_node', self.orthographic_lens)

        application.base.cam.node().set_lens(self.lens)

        self.orthographic = False
        self.fov = 40   # horizontal fov
        self.clip_plane_near = 0.1
        self.clip_plane_far = 10000

        self.ui_display_region = win.make_display_region()
        self.ui_display_region.set_sort(20)

        self.ui_camera = NodePath(PandaCamera('ui_camera'))
        self.ui_lens = OrthographicLens()
        # moved set_film_size() to window module for correct aspect ratio after setting window size
        self.ui_lens.set_near_far(-1000, 1000)
        self.ui_camera.node().set_lens(self.ui_lens)
        self._ui_lens_node = LensNode('_ui_lens_node', self.ui_lens)

        self.ui_render = NodePath('ui_render')
        self.ui_render.set_depth_test(0)
        self.ui_render.set_depth_write(0)
        self.ui_camera.reparent_to(self.ui_render)
        self.ui_display_region.set_camera(self.ui_camera)
        scene.ui_camera = self.ui_camera

        self.ui.parent = self.ui_camera

        # these get created when setting a shader
        self.filter_manager = None
        self.filter_quad = None
        self.render_texture = None
        self.filter_quad = None
        self.depth_texture = None


    def orthographic_getter(self):
        return getattr(self, '_orthographic', False)

    def orthographic_setter(self, value):
        self._orthographic = value
        self.lens_node = (self.perspective_lens_node, self.orthographic_lens_node)[value] # this need to be set for the mouse raycasting
        application.base.cam.node().set_lens((self.perspective_lens, self.orthographic_lens)[value])
        self.fov = self.fov

    def fov_getter(self):
        return getattr(self, '_fov', 0)
    def fov_setter(self, value):
        value = max(1, value)
        self._fov = value
        if not self.orthographic and hasattr(self, 'perspective_lens'):
            self.perspective_lens.set_fov(value)
            # self.perspective_lens.set_fov(value*window.aspect_ratio, value)

        elif self.orthographic and hasattr(self, 'orthographic_lens'):
            self.orthographic_lens.set_film_size(value * self.aspect_ratio, value)

    def clip_plane_near_getter(self):
        return self._clip_plane_near
    def clip_plane_near_setter(self, value):
        self._clip_plane_near = value
        self.lens.set_near(value)

    def clip_plane_far_getter(self):
        return self._clip_plane_far
    def clip_plane_far_setter(self, value):
        self._clip_plane_far = value
        self.lens.set_far(value)


    def aspect_ratio_getter(self):
        return self.perspective_lens.get_aspect_ratio()


    def shader_setter(self, value):
        self._shader = value
        if value is None:
            self.filter_manager.cleanup()
            self.filter_manager = None
            if self.filter_quad:
                self.filter_quad.removeNode()
                # print('removed shader')
            return None

        shader = value

        if isinstance(value, Shader) and not shader.compiled:
            shader.compile()

        if isinstance(value, Shader):
            shader = shader._shader

        if not self.filter_manager:
            self.filter_manager = FilterManager(application.base.win, application.base.cam)
            self.render_texture = PandaTexture()
            self.depth_texture = PandaTexture()
            # self.normals_texture = PandaTexture()
            # from panda3d.core import AuxBitplaneAttrib
            self.filter_quad = self.filter_manager.renderSceneInto(
                colortex=self.render_texture,
                depthtex=self.depth_texture,
                # auxtex=self.normals_texture,
                # auxbits=AuxBitplaneAttrib.ABOAuxNormal
                )
            self.filter_quad.set_shader_input("tex", self.render_texture)
            self.filter_quad.set_shader_input("dtex", self.depth_texture)

            self.clip_plane_near = 1
            # self.filter_quad.set_shader_input("ntex", self.normals_texture)

        self.filter_quad.setShader(shader)

        if hasattr(value, 'default_input'):
            for key, value in value.default_input.items():
                if callable(value):
                    value = value()

                self.set_shader_input(key, value)


        print_info('set camera shader to:', shader)


    def set_shader_input(self, name, value):
        if not hasattr(self, 'filter_quad') or self.filter_quad is None:
            return

        if isinstance(value, Texture):
            value = value._texture    # make sure to send the panda3d texture to the shader

        self.filter_quad.setShaderInput(name, value)


instance = Camera()


if __name__ == '__main__':
    from ursina import *
    from ursina import Ursina, camera, Entity, EditorCamera

    # window.borderless = False
    app = Ursina()

    camera.orthographic = True

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

    EditorCamera()
    # from ursina import *
    # Button(text='test button')
    from ursina.shaders import camera_grayscale_shader
    camera.shader = camera_grayscale_shader

    # def update():
    #     t = Texture(camera.render_texture)
    #     print(t.pixels)
    app.run()
