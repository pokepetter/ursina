from ursina import *


class SplashScreen(Sprite):
    def __init__(self, texture='ursina_logo', **kwargs):
        super().__init__(parent=camera.ui, texture=texture, world_z=camera.overlay.z-1, scale=.1, color=color.clear, **kwargs)
        camera.overlay.animate_color(color.black, duration=.1)
        self.animate_color(color.white, duration=2, delay=1, curve=curve.out_quint_boomerang)
        invoke(destroy, self, delay=3)


    def input(self, key):
        if key in ('space', 'gamepad a', 'escape', 'left mouse down'):
            destroy(self)


    def on_destroy(self):
        camera.overlay.animate_color(color.clear, duration=.25)



if __name__ == '__main__':
    app = Ursina()

    ursina_splash = SplashScreen()
    # add a custom splash screen after the first one
    ursina_splash.on_destroy = Func(SplashScreen, 'shore')
    app.run()
