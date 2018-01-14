from pandaeditor import *

class Sky(Entity):

    def __init__(self, texture_name_arg='default_sky'):
        super.__init__()
        self.name = 'sky'
        self.sky.scale *= 9999
        self.sky.model = 'sky_dome'
        # self.sky.color = color.gray
        self.sky.texture = texture_name_arg
