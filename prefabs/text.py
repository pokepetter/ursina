import sys
sys.path.append("..")
from pandaeditor import *
import time



class Text(Entity):


    def __init__(self):
        super().__init__()
        self.name = 'text'
        # self.parent = scene.ui
        self.model = 'quad'
        self.background_color = color.clear
        # self.color = color.smoke
        self.character_spacing = .25
        self.font_size = 1
        self.text = ''
        self.characters = list()


    def update_text(self):
        start_time = time.time()
        char_entity = Entity()
        # char_entity.name = 'char_temp'
        char_entity.parent = self.model
        char_entity.model = 'quad'
        # char_entity.scale = (1,1,1)
        # char_entity.color = color.blue
        # char_entity.wrtReparentTo(self.model)
        width = char_entity.getScale()[0]
        # height = char_entity.getScale()[2]
        height = width
        # self.model.setScale(.1,.1,.1)
        destroy(char_entity)

        self.x = -(len(self.text) * self.character_spacing /10) + self.character_spacing / 5
        # self.x = - (width * self.character_spacing) + width * self.character_spacing

        x = 0
        y = 0
        for i in range(len(self.text)):
            # if self.text[i] == ' ':
            #     pass
            if self.text[i] == ' ':
                pass
            elif self.text[i] == '\n':
                y -= 1
                x = 0
            else:
                self.char_entity = loader.loadModel('models/' + 'quad' + '.egg')
                self.char_entity.reparentTo(self)
                self.char_entity.setColorScaleOff()
                self.char_entity.setPos(Vec3(x * width * self.character_spacing, 1, y * height))

                self.characters.append(self.char_entity)

                try:
                    char_name = '_' + self.text[i]
                    if char_name.isupper():
                        char_name += 'u'

                    # char_entity.texture = 'textures/font/' + char_name + '.png'
                    texture = loader.loadTexture('textures/font/' + char_name + '.png')
                    self.char_entity.setTexture(texture, 1)
                    # if self.color:
                    #     char_entity.color = self.color
                except:
                    pass # missing character

            x += 1
            if x > 50:
                y -= 1
                x = 0

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
        if name == 'background_color':
            self.model.setColorScale(value)
        if name == 'align':
            if value == 'left':
                print('prant scale x:', self.parent.scale_x)
        elif name == 'color':
            self.update_colors(value)
        else:
            super().__setattr__(name, value)

    #
    # def __getattr__(self, attrname):
    #     try:
    #         return self.attrname
    #     except:
    #         pass
