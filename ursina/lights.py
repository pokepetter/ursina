from ursina import *
from panda3d.core import DirectionalLight as PandaDirectionalLight
from panda3d.core import PointLight as PandaPointLight
from panda3d.core import AmbientLight as PandaAmbientLight
from panda3d.core import Spotlight as PandaSpotLight


class Light(Entity):
    def __init__(self, **kwargs):
        super().__init__(rotation_x=90)


    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._light.setColor(value)


class DirectionalLight(Light):
    def __init__(self, shadows=True, **kwargs):
        super().__init__()
        self._light = PandaDirectionalLight('directional_light')
        render.setLight(self.attachNewNode(self._light))
        self.shadow_map_resolution = Vec2(1024, 1024)

        for key, value in kwargs.items():
            setattr(self, key ,value)

        invoke(setattr, self, 'shadows', shadows, delay=.1)


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
        bmin, bmax = entity.get_tight_bounds(self)
        lens = self._light.get_lens()
        lens.set_near_far(bmin.z*2, bmax.z*2)
        lens.set_film_offset((bmin.xy + bmax.xy) * .5)
        lens.set_film_size(bmax.xy - bmin.xy)


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
    app = Ursina()
    from ursina.shaders import lit_with_shadows_shader # you have to apply this shader to enties for them to receive shadows.
    EditorCamera()
    Entity(model='plane', scale=10, color=color.gray, shader=lit_with_shadows_shader)
    Entity(model='cube', y=1, shader=lit_with_shadows_shader)
    pivot = Entity()
    DirectionalLight(parent=pivot, y=2, z=3, shadows=True)


    app.run()
