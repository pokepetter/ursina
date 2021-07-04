from ursina import *
from direct.stdpy import thread


class LoadingWheel(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.parent = camera.ui
        self.point = Entity(parent=self, model=Circle(24, mode='point', thickness=.03), color=color.light_gray, y=.75, scale=2, texture='circle')
        self.point2 = Entity(parent=self, model=Circle(12, mode='point', thickness=.03), color=color.light_gray, y=.75, scale=1, texture='circle')

        self.scale = .025
        self.text_entity = Text(world_parent=self, text='loading...', origin=(0,1.5), color=color.light_gray)
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
    info_text = Text('''Press space to start loading textures''', origin=(0,0), color=color.black)
    loading_screen = LoadingWheel(enabled=False)
    from ursina.prefabs.health_bar import HealthBar

    def load_textures():
        textures_to_load = ['brick', 'shore', 'grass', 'heightmap'] * 50
        bar = HealthBar(max_value=len(textures_to_load), value=0, position=(-.5,-.35,-2), scale_x=1, animation_duration=0, world_parent=loading_screen, bar_color=color.gray)
        for i, t in enumerate(textures_to_load):
            load_texture(t)
            print(i)
            bar.value = i+1
        # destroy(bar, delay=.01)
        print('loaded textures')
        loading_screen.enabled = False

    def input(key):
        if key == 'space':
            loading_screen.enabled = True
            info_text.enabled = False
            t = time.time()

            try:
                thread.start_new_thread(function=load_textures, args='')
            except Exception as e:
                print('error starting thread', e)

            print('---', time.time()-t)
    # load_textures()
    # invoke(load_textures, delay=0)
    app.run()
