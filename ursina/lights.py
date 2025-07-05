from ursina import Entity, Vec2, invoke, scene, color, Vec3, print_warning
from ursina.prefabs.sky import Sky
from panda3d.core import DirectionalLight as PandaDirectionalLight
from panda3d.core import PointLight as PandaPointLight
from panda3d.core import AmbientLight as PandaAmbientLight
from panda3d.core import Spotlight as PandaSpotLight


class Light(Entity):
    default_values = {'rotation_x':90, }
    def __init__(self, **kwargs):
        super().__init__(**(__class__.default_values | kwargs))

    @property
    def color(self):
        return getattr(self, '_color', color.white)

    @color.setter
    def color(self, value):
        self._color = value
        self._light.setColor(value)

from ursina.scripts.property_generator import generate_properties_for_class


@generate_properties_for_class()
class DirectionalLight(Light):
    def __init__(self, shadow_map_resolution=Vec2(1024,1024), shadows=True, **kwargs):
        super().__init__(**kwargs)
        self._light = PandaDirectionalLight('directional_light')
        node_path = self.attachNewNode(self._light)
        node_path.node().setCameraMask(0b0001)
        render.setLight(node_path)

        self.shadow_map_resolution = shadow_map_resolution
        self._bounds_entity = scene
        self.shadows = shadows

    def shadows_setter(self, value):
        self._shadows = value
        if value:
            self._light.set_shadow_caster(True, int(self.shadow_map_resolution[0]), int(self.shadow_map_resolution[1]))
            self.update_bounds()
        else:
            self._light.set_shadow_caster(False)



    def update_bounds(self, entity=scene):  # update the shadow area to fit the bounds of target entity, defaulted to scene.
        # don't include skydome when calculating shadow bounds
        [e.disable() for e in Sky.instances]

        bounds = entity.get_tight_bounds(self)
        if bounds is not None:
            bmin, bmax = bounds
            lens = self._light.get_lens()
            lens.set_near_far(bmin.z*2, bmax.z*2)
            lens.set_film_offset((bmin.xy + bmax.xy) * .5)
            lens.set_film_size(bmax.xy - bmin.xy)
        else:
            lens = self._light.get_lens()
            lens.set_near_far(1, 100)
            lens.set_film_offset((0, 0))
            lens.set_film_size((1, 1))

        [e.enable() for e in Sky.instances]

        self._bounds_entity = entity

    def look_at(self, target, axis=Vec3.forward):
        super().look_at(target, axis=axis)
        self.update_bounds(self._bounds_entity)



class PointLight(Light):
    def __init__(self, **kwargs):
        super().__init__()
        self._light = PandaPointLight('point_light')
        render.setLight(self.attachNewNode(self._light))

        for key, value in kwargs.items():
            setattr(self, key ,value)



class AmbientLight(Light):
    def __init__(self, **kwargs):
        super().__init__()
        self._light = PandaAmbientLight('ambient_light')
        render.setLight(self.attachNewNode(self._light))

        for key, value in kwargs.items():
            setattr(self, key ,value)



class SpotLight(Light):
    def __init__(self, **kwargs):
        super().__init__()
        self._light = PandaSpotLight('spot_light')
        render.setLight(self.attachNewNode(self._light))

        for key, value in kwargs.items():
            setattr(self, key ,value)




if __name__ == '__main__':
    from ursina import Ursina, EditorCamera, color, Vec3
    from ursina.shaders import lit_with_shadows_shader # you have to apply this shader to enties for them to receive shadows.

    app = Ursina()

    Entity.default_shader = lit_with_shadows_shader
    ground = Entity(model='plane', scale=10, texture='grass')
    lit_cube = Entity(model='cube', y=1, color=color.light_gray)

    light = DirectionalLight()
    light.look_at(Vec3(1,-1,1))

    dont_cast_shadow = Entity(model='cube', y=1, x=2, color=color.light_gray)
    dont_cast_shadow.hide(0b0001)

    unlit_entity = Entity(model='cube', y=1,x=-2, unlit=True, color=color.light_gray)

    bar = Entity(model='cube', position=(0,3,-2), scale=(10,.2,.2), color=color.light_gray)
    # dont_cast_shadow.hide(0b0001)

    # How to render shows in a limited area.
    # to make it easier to see, make a box to define where we will have shadows. we can make this invisible after.
    shadow_bounds_box = Entity(model='wireframe_cube', scale=5, visible=0)
    light.update_bounds(shadow_bounds_box)

    EditorCamera(rotation=(30,30,0))
    Sky()
    # from ursina import window
    # window.borderless = True
    # window.size = Vec2(1920,1080) * .5
    # window.editor_ui.enabled = False
    app.run()
