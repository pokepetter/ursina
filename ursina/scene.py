import sys
from panda3d.core import NodePath
from panda3d.core import Fog
from ursina import color
from ursina.texture_importer import load_texture
# from ursina.ursinastuff import destroy
# from ursina.entity import Entity


class Scene(NodePath):

    def __init__(self):
        super().__init__('scene')
        self.render = None
        self.world = None

        self.camera = None
        self.ui_camera = None
        self.canvas = None
        self.ui = None

        self.entities = []
        self.hidden = NodePath('hidden')
        self.reflection_map = 'reflection_map_3'


    def set_up(self):
        from ursina.entity import Entity
        self.reparent_to(render)
        self.reflection_map = load_texture(self.reflection_map)

        self.fog = Fog('fog')
        self.setFog(self.fog)
        self.fog_color = color.light_gray
        self.fog_density = 0


    def clear(self):
        from ursina.ursinastuff import destroy
        to_destroy = [e for e in self.entities if not e.eternal]
        to_keep = [e for e in self.entities if e.eternal]

        for d in to_destroy:
            try:
                print('destroying:', d.name)
                destroy(d)
            except Exception as e:
                print('failed to destroy entity', e)


        self.entities = to_keep

        from ursina import application
        application.sequences.clear()


    @property
    def fog_color(self):
        return self.fog.getColor()

    @fog_color.setter
    def fog_color(self, value):
        self.fog.setColor(value)


    @property
    def fog_density(self):
        return self._fog_density

    @fog_density.setter
    def fog_density(self, value):
        self._fog_density = value
        if isinstance(value, tuple):     # linear fog
            self.fog.setLinearRange(value[0], value[1])
        else:
            self.fog.setExpDensity(value)


sys.modules[__name__] = Scene()



if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    # yolo = Button(name='yolo', text='yolo')
    e = Entity(model='plane', color=color.black, scale=100)
    EditorCamera()
    s = Sky()

    def input(key):
        if key == 'l':
            for e in scene.entities:
                print(e.name)

        if key == 'd':
            scene.clear()

    scene.fog_density = .1          # sets exponential density
    scene.fog_density = (50, 200)   # sets linear density start and end

    app.run()
