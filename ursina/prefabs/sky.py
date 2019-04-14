from ursina import *

class Sky(Entity):

    def __init__(self, **kwargs):
        super().__init__()
        self.name = 'sky'
        self.scale *= 9900
        self.model = 'sky_dome'
        self.texture = 'default_sky'

        for key, value in kwargs.items():
            setattr(self, key, value)


        def update(self):
            self.world_position = camera.world_position

if __name__  == '__main__':
    app = Ursina()
    test = load_prefab('sky')
    app.run()
