from pandaeditor import *


class UI():

    def __init__(self):
        self.entity = None

    def fit_to_screen(self):
        screen_height = math.tan((math.pi / 180) * (40 * 1)) * distance(self.entity.node_path.getPos(render), camera.cam.getPos(render));
        aspect_ratio = screen_size[0] / screen_size[1]
        self.entity.scale = (self.entity.scale[0] * screen_height * aspect_ratio, 1, self.entity.scale[2] * screen_height)


    def input(self, key):
        if key == 'tab':
            # print(self.entity.node_path.getChildren())
            for c in self.entity.node_path.getChildren():
                print(c.entity.name)
            # self.entity.enabled = not self.entity.enabled

    def panel(self):
        entity = Entity()
        entity.name = 'panel'
        entity.parent = ui_entity.node_path
        entity.model = loader.loadModel('models/quad.egg')
        tex = loader.loadTexture('textures/sketch_2.png')
        entity.model.setTexture(tex, 1)
        entity.position = (0, 0, 0.0)
        entity.scale = (1, 1, 1)
        self.entity.parent.entities.append(entity)
        return entity

# sys.modules[__name__] = UI()
