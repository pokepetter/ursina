from ursina import *

if __name__ == '__main__':
    app = Ursina()

camera.overlay.fade_in(duration=0)
logo = Sprite(name='ursina_splash', parent=camera.ui, texture='ursina_logo', world_z=camera.overlay.z-1, scale=.1, color=color.clear)
logo.animate_color(color.white, duration=1, delay=.0)
logo.fade_out(.5, delay=5, curve=curve.linear)
camera.overlay.animate_color(color.clear, duration=1, delay=5)
destroy(logo, delay=5)

if __name__ == '__main__':
    app.run()
