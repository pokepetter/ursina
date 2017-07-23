import sys
sys.path.append("..")
from pandaeditor import *

class Text(Entity):


    def __init__(self):
        super().__init__()
        self.name = 'text'
        self.parent = scene.ui.entity.node_path
        self.model = loader.loadModel('models/quad.egg')
        # self.model.hide()
        # self.collision = True
        # self.collider = (self.model.getPos(scene.render), # pos
        #                 (0,0,0), # rot
        #                 (self.model.getScale(scene.render)[0] /4,
        #                 1,
        #                 self.model.getScale(scene.render)[2] /4))
        self.text = ''
        self.character_spacing = .45

        scene.entities.append(self)

    def update_text(self):
        char_entity = load_prefab('panel')
        char_entity.parent = scene.render
        char_entity.scale = (1,1,1)
        char_entity.node_path.wrtReparentTo(self.model)
        width = char_entity.node_path.getScale()[0]
        height = char_entity.node_path.getScale()[2]
        destroy(char_entity)

        x = 0
        z = 0
        for i in range(len(self.text)):
            if self.text[i] != ' ':
                char_entity = load_prefab('panel')
                char_entity.parent = scene.render
                char_entity.scale = (1,1,1)
                char_entity.node_path.wrtReparentTo(self.model)
                char_entity.origin = (-.5, 0, .5)
                char_entity.position = (-.5 + (x * width * self.character_spacing),
                                        -.1,
                                        (z * height) + .5)

                try:
                    char_name = '_' + self.text[i]
                    if char_name.isupper():
                        char_name += 'u'
                    char_entity.texture = 'textures/font/' + char_name + '.png'
                    char_entity.color = self.color
                except:
                    pass # missing character
            # char_entity.color = color.hsv_color(i * 10, 1, 1)

            x += 1
            if x > 30:
                z -= 1
                x = 0


    def __setattr__(self, name, value):
        if name == 'position':
            value = tuple(x / 2 for x in value)
        if name == 'text':
            object.__setattr__(self, name, value)
            self.update_text()
        if name == 'scale' and self.model and self.collision:
            super().__setattr__(name, value)
            self.collider = (self.model.getPos(scene.render), (0,0,0),
                            (self.model.getScale(scene.render)[0] /4, 1,
                            self.model.getScale(scene.render)[2] /4))

        # if name != 'color':
        super().__setattr__(name, value)
