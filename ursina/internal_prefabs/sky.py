from ursina import *

class Sky(Entity):

    def __init__(self, texture_name_arg='default_sky'):
        super().__init__()
        self.name = 'sky'
        self.scale *= 9999
        self.model = 'sky_dome'
        # self.color = color.gray
        self.texture = texture_name_arg


if __name__  == '__main__':
    app = Ursina()
    test = load_prefab('sky')
    app.run()
