from ursina import *
from direct.stdpy import thread


class LoadingWheel(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.parent = camera.ui
        self.point = Entity(
            parent=self,
            model=Circle(24, mode='point', thickness=3),
            color=color.light_gray,
            y=.75,
            scale=2
            )
        self.point2 = Entity(
            parent=self,
            model=Circle(12, mode='point', thickness=3),
            color=color.light_gray,
            y=.75,
            scale=1
            )
        self.scale = .025
        self.text_entity = Text(
            world_parent = self,
            text = '  loading...',
            origin = (0,1.5),
            color = color.light_gray,
            )
        self.y = -.25

        self.bg = Entity(parent=self, model='quad', scale_x=camera.aspect_ratio, color=color.black, z=1)
        self.bg.scale *= 400

        for key, value in kwargs.items():
            setattr(self, key ,value)


    def update(self):
        self.point.rotation_y += 5
        self.point2.rotation_y += 3

if __name__ == '__main__':
    app = Ursina()
    window.color = color.white
    loading_screen = LoadingWheel(enabled=False)
    from ursina.prefabs.health_bar import HealthBar

    def load_textures():
        for i in range(9999):
            print('lolo'+'lol')
        # window.color=color.white
        return

        textures_to_load = ['brick', 'shore', 'grass', 'heightmap'] * 100
        bar = HealthBar(max_value=len(textures_to_load), value=0, position=(0,0,-1))
        for i, t in enumerate(textures_to_load):
            load_texture(t)
            print(i)
            bar.value = i+1
            print('loaded textturres')
        # destroy(bar, delay=.01)

    def input(key):
        if key == 'space':
            loading_screen.enabled = True
            # window.color=color.black
            # t = time.time()
            # try:
            #     thread.start_new_thread(target=load_textures)
            # except:
            #     print('error starting thread')

            load_textures()
            loading_screen.enabled = False
            print('---', time.time()-t)
    # load_textures()
    # invoke(load_textures, delay=0)
    app.run()
