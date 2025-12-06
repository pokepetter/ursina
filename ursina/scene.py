from panda3d.core import NodePath, Fog
from ursina import color


class Scene(NodePath):
    def __init__(self):
        super().__init__('scene')
        self.entities = []
        self._entities_marked_for_removal = []
        self.collidables = set()
        self._children = []
        self.fog = Fog('fog')
        self.setFog(self.fog)
        self.fog_color = color.clear
        self.fog_density = 0

    def _set_up(self):
        self.reparent_to(render)


    def clear(self):
        from ursina import application, destroy

        to_destroy = [e for e in self.entities if not e.eternal]
        to_keep = [e for e in self.entities if e.eternal]

        for d in to_destroy:
            try:
                destroy(d)
            except Exception as e:
                print('failed to destroy entity', e)

        self.entities = to_keep
        application.sequences.clear()


    @property
    def fog_color(self):
        return self._fog_color
    @fog_color.setter
    def fog_color(self, value):
        self._fog_color = value
        self.fog.setColor(value)
        # for c in self.children:     # scene is just pretending to be an entity, so have to do this
        #     for e in c.get_descendants():
        for e in self.entities:
            try:
                from ursina.camera import instance as camera
                if e.has_ancestor(camera.ui):
                    continue
            except:
                pass

            if e in self._entities_marked_for_removal:
                continue
            if e.shader and 'fog_color' in e.shader.default_input:
                e.set_shader_input('fog_color', value)


    @property
    def fog_density(self):
        return self._fog_density

    @fog_density.setter     # set to (start, end) for linear fog.
    def fog_density(self, value):
        self._fog_density = value
        if isinstance(value, tuple):     # linear fog
            self.fog.setLinearRange(value[0], value[1])
            for e in self.entities:
                try:
                    from ursina.camera import instance as camera
                    if e.has_ancestor(camera.ui):
                        continue
                except:
                    pass

                if e in self._entities_marked_for_removal:
                    continue
                if e.shader and 'fog_start' in e.shader.default_input and 'fog_end' in e.shader.default_input:
                    e.set_shader_input('fog_start', value[0])
                    e.set_shader_input('fog_end', value[1])
        # else:
        #     self.fog.setExpDensity(value)

    @property
    def children(self):
        return [e for e in self._children if e]     # make sure list doesn't contain destroyed entities

    @children.setter
    def children(self, value):
        self._children = value


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


    from ursina.shaders.unlit_with_fog_shader import unlit_with_fog_shader
    e = Entity(model='cube', shader=unlit_with_fog_shader)
    # scene.fog_density = .1          # sets exponential density
    unlit_with_fog_shader.fog_color = color.blue
    unlit_with_fog_shader.fog_density = (0,100)

    # scene.fog_density = (0, 200)   # sets linear density start and end
    # scene.fog_color = color.green
    Entity(parent=camera.ui, model='quad', scale=.1)

    app.run()
