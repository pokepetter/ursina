import sys
import time
sys.path.append("..")
from pandaeditor import *
from panda3d.core import TransparencyAttrib

from os import path
from panda3d.core import Filename


class Text(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'text'
        self.model = 'quad'
        self.color = color.clear
        self.character_spacing = .5
        self.line_height = 1
        self.character_limit = 50
        self.text = ''
        self.size = 1
        self.characters = list()
        self.scale *= 0.355
        self.origin = (0, 0)
        self.x = 0


    def update_text(self):
        start_time = time.time()

        if self.characters:
            for c in self.characters:
                c.removeNode()

        x = 0
        y = 0
        for i in range(len(self.text)):

            if self.text[i] == ' ' or self.text[i] == '\\' :
                pass
            elif self.text[i] == '\n':
                y -= self.line_height
                x = -1
            else:
                self.char_entity = loader.loadModel('internal_models/' + 'quad' + '.egg')
                self.char_entity.reparentTo(self.model)

                self.char_entity.setPos(Vec3(
                    x * 1 * self.size * self.character_spacing,
                    -.1,
                    (y * 1 * self.size * self.line_height)))
                self.char_entity.setScale(self.size)

                self.characters.append(self.char_entity)

                try:
                    char_name = '_' + self.text[i]
                    if char_name.isupper():
                        char_name += 'u'

                    texture = loader.loadTexture(
                        Filename.fromOsSpecific(
                            (path.join(
                                path.dirname(path.dirname(__file__)),
                                'font/')
                             + char_name + '.png')))

                    self.char_entity.setColorScaleOff()
                    self.char_entity.setTransparency(TransparencyAttrib.MAlpha)
                    self.char_entity.setTexture(texture, 1)
                except:
                    pass # missing character

            x += 1
            if x > self.character_limit:
                x = 0
                y -= 1

        try:
            self.set_origin(self.origin)
        except:
            pass
        # print("--- %s seconds ---" % (time.time() - start_time))

    def set_origin(self, origin):
        self.width = min(len(self.characters), self.character_limit)
        self.width *= self.character_spacing

        # test = Entity()
        # test.parent = self.model
        # test.model = 'quad'
        # test.color = color.white33
        # test.origin = (-.5, 0)
        # test.position = (-.25,0)
        # test.scale_x = self.width

        # -.5     - self.width * 1
        # 0       - self.width * .5
        # .5      - self.width * 0

        self.model.setPos(
            - (self.width * ((-self.origin[0] - .5) * -1)) + .25,
            0,
            0)

        # self.model.setPos(
        #     - ((origin[0] * 2) * self.width) - 1,
        #     0,
        #     0)

    def appear(self, interval):
        for char in self.characters:
            char.node_path

    def update_colors(self, value):
        if hasattr(self, 'characters'):
            print('updating colors')
            for char in self.characters:
                char.color = value



    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except:
            pass

        if name == 'text':
            object.__setattr__(self, name, value)
            self.update_text()

        if name == 'origin':
            object.__setattr__(self, name, value)
            try:
                self.set_origin(self.origin)
            except:
                pass
        #     self.update_text()
        if name == 'size':
            object.__setattr__(self, name, value)
            self.update_text()
