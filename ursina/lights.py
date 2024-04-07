from ursina import Entity, Vec2, invoke, scene, color
from ursina.prefabs.sky import Sky
from panda3d.core import DirectionalLight as PandaDirectionalLight
from panda3d.core import PointLight as PandaPointLight
from panda3d.core import AmbientLight as PandaAmbientLight
from panda3d.core import Spotlight as PandaSpotLight


class Light(Entity):
    def __init__(self, **kwargs):
        super().__init__(rotation_x=90, **kwargs)


    @property
    def color(self):
        return getattr(self, '_color', color.white)

    @color.setter
    def color(self, value):
        self._color = value
        self._light.setColor(value)


class DirectionalLight(Light):
    def __init__(self, shadows=True, **kwargs):
        super().__init__()
        self._light = PandaDirectionalLight('directional_light')
        node_path = self.attachNewNode(self._light)
        node_path.node().setCameraMask(0b0001)
        render.setLight(node_path)
        self.shadow_map_resolution = Vec2(1024, 1024)

        for key, value in kwargs.items():
            setattr(self, key ,value)

        invoke(setattr, self, 'shadows', shadows, delay=1/60)


    @property
    def shadows(self):
        return self._shadows

    @shadows.setter
    def shadows(self, value):
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

        [e.enable() for e in Sky.instances]


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

    app = Ursina()
    from ursina.shaders import lit_with_shadows_shader # you have to apply this shader to enties for them to receive shadows.
    EditorCamera()
    Entity(model='plane', scale=10, color=color.gray, shader=lit_with_shadows_shader)
    Entity(model='cube', y=1, shader=lit_with_shadows_shader, color=color.light_gray)
    light = DirectionalLight(shadows=True)
    light.look_at(Vec3(1,-1,1))

    dont_cast_shadow = Entity(model='cube', y=1, shader=lit_with_shadows_shader, x=2, color=color.light_gray)
    dont_cast_shadow.hide(0b0001)

    unlit_entity = Entity(model='cube', y=1,x=-2, unlit=True, color=color.light_gray)

    bar = Entity(model='cube', position=(0,3,-2), shader=lit_with_shadows_shader, scale=(10,.2,.2), color=color.light_gray)
    # dont_cast_shadow.hide(0b0001)

    app.run()
