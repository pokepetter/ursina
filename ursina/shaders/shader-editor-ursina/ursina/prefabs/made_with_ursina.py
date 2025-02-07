from ursina import *



if __name__ == '__main__':
    app = Ursina()
    window.color=color._10
    t = Text('''powered by\nursina engine\nʕ •ᴥ•ʔゝ□''', font='unifont.ttf', scale=3, origin=(0,0))
    t.appear(speed=.05)
    t.fade_out(delay=3, duration=1, curve=curve.linear)
    # Sprite(texture='default_sky', z=1, color=color.dark_gray)
    Entity(parent=camera.ui, model='quad', texture='shore', scale_x=1.777)
    Text('Shore of Shadows', origin=(0,0), scale=6, color=color._20, y=.15, resolution=300)
    app.run()
