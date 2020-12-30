from ursina import *

if __name__ == '__main__':
    app = Ursina()

camera.overlay.color = color.black
logo = Sprite(name='ursina_splash', parent=camera.ui, texture='ursina_logo', world_z=camera.overlay.z-1, scale=.1, color=color.clear)
logo.animate_color(color.white, duration=2, delay=1, curve=curve.out_quint_boomerang)
camera.overlay.animate_color(color.clear, duration=1, delay=4)
destroy(logo, delay=5)

def splash_input(key):
    destroy(logo)
    camera.overlay.animate_color(color.clear, duration=.25)

logo.input = splash_input



if __name__ == '__main__':
    app.run()
