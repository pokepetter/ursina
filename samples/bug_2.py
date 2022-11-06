from ursina import *

app = Ursina()

def update():
    print(held_keys['gamepad left stick x'])


app.run()
