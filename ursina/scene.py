import sys
from panda3d.core import NodePath
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
        self.has_changes = False
        self.reflection_map = 'reflection_map_3'

    def set_up(self):
        from ursina.entity import Entity
        self.reparent_to(render)
        self.reflection_map = load_texture(self.reflection_map)


    def clear(self):
        from ursina.ursinastuff import destroy
        to_destroy = [e for e in self.entities if not e.eternal]
        to_keep = [e for e in self.entities if e.eternal]

        for d in to_destroy:
            print('destroying:', d.name)
            destroy(d)

        self.entities = to_keep

        from ursina import application
        application.sequences.clear()


sys.modules[__name__] = Scene()



if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    yolo = Button(name='yolo', text='yolo')

    def input(key):
        if key == 'd':
            scene.clear()
    app.run()
