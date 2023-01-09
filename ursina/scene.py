from panda3d.core import NodePath, Fog
from ursina import color


class Scene(NodePath):

    def __init__(self):
        super().__init__('scene')
        self.entities = []


    def set_up(self):
        self.reparent_to(render)
        self.fog = Fog('fog')
        self.setFog(self.fog)
        self.fog_color = color.light_gray
        self.fog_density = 0


    def clear(self):
        from ursina.ursinastuff import destroy
        from ursina import application

        [destroy(e) for e in self.entities if not e.eternal]
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

    @fog_density.setter     # set to a number for exponential density or (start, end) for linear.
    def fog_density(self, value):
        self._fog_density = value
        if isinstance(value, tuple):     # linear fog
            self.fog.setLinearRange(value[0], value[1])
        else:
            self.fog.setExpDensity(value)


instance = Scene()



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
            Entity(model='cube')

    scene.fog_density = .1          # sets exponential density
    scene.fog_density = (50, 200)   # sets linear density start and end

    app.run()
