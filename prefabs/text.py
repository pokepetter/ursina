import sys
sys.path.append("..")
from pandaeditor import *
import time
from panda3d.core import TransparencyAttrib



class Text(Entity):


    def __init__(self):
        super().__init__()
        self.name = 'text'
        self.color = color.blue
        self.character_spacing = .25
        self.line_height = .5
        self.font_size = 1
        self.character_limit = 50
        self.text = ''
        self.characters = list()
        # self.scale = (.75,.75,.75)


    def update_text(self):
        start_time = time.time()

        x = 0
        y = 0
        for i in range(len(self.text)):
            # if self.text[i] == ' ':
            #     pass
            if self.text[i] == ' ':
                pass
            elif self.text[i] == '\n':
<<<<<<< HEAD
                y -= self.line_height
                x = -1
=======
                y -= height
                x = 0
>>>>>>> bd5b1195df5f328f76a54053b490dd948e264f81
            else:
                self.char_entity = loader.loadModel('models/' + 'quad' + '.egg')
                self.char_entity.reparentTo(self)
                self.char_entity.setPos(Vec3(
                    (x * 1 * self.font_size * self.character_spacing),
                    -.1,
                    (y * 1 * self.font_size * self.line_height)))
                self.char_entity.setScale(self.font_size)
                # self.char_entity.setColorScaleOff()
                self.char_entity.setColorScale(color.blue)

                self.characters.append(self.char_entity)

                try:
                    char_name = '_' + self.text[i]
                    if char_name.isupper():
                        char_name += 'u'

                    # char_entity.texture = 'textures/font/' + char_name + '.png'
                    texture = loader.loadTexture('textures/font/' + char_name + '.png')
                    self.char_entity.setColorScaleOff()
                    self.char_entity.setTransparency(TransparencyAttrib.MAlpha)
                    self.char_entity.setTexture(texture, 1)
                    # if self.color:
                    #     char_entity.color = self.color
                except:
                    pass # missing character

            x += 1
            if x > self.character_limit:
                x = 0
                y -= 1

        print("--- %s seconds ---" % (time.time() - start_time))

    def appear(self, interval):
        for char in self.characters:
            char.node_path

    def update_colors(self, value):
        if hasattr(self, 'characters'):
            print('updating colors')
            for char in self.characters:
                char.color = value

    def align(self, value):
        pass
        # for char in self.characters:
        #     if value ==
        #     char.color = value


    def __setattr__(self, name, value):
        if name == 'position':
            value = tuple(x / 2 for x in value)
        if name == 'text':
            object.__setattr__(self, name, value)
            self.update_text()
        if name == 'scale':
            super().__setattr__(name, value)
        if name == 'align':
            if value == 'left':
                print('prant scale x:', self.parent.scale_x)
        # elif name == 'color':
        #     self.update_colors(value)
        else:
            super().__setattr__(name, value)

    #
    # def __getattr__(self, attrname):
    #     try:
    #         return self.attrname
    #     except:
    #         pass
