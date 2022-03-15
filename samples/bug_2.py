from venv import create
from ursina import *

app = Ursina()
def window_ursina():
    # window.fullscreen_size =(3840,2160)
    window.title = 'Katalog eksponatów \U0001F600'     # The window title
    window.borderless = False               # Show a border
    window.fullscreen = False               # Do not go Fullscreen
    window.exit_button.visible = False      # Do not show the in-game red X that loses the window
    window.fps_counter.enabled = False

BUTTONS_NUMBER = 50

def create_buttons(quantity):
    button_list = {}
    for i in range(0, quantity):
        button_list[f"<white>button{i}"] = Func(print, i)
    return button_list
def on_slider_change():
    button_list.y = .27 + ((slider.value) * ((button_list.scale_y * BUTTONS_NUMBER)/100))
button_list = ButtonList(create_buttons(BUTTONS_NUMBER), button_height= 1.618 * 1.5, width=.35)
button_list.text_entity.y = -Text.size/4
slider = ThinSlider(
    default= 0,
    min = 1, max = 0,
    dynamic = True,
    x = -.5, y=-.25,
    step=0.01,
    vertical = True,
    on_value_changed=on_slider_change
)

window_ursina()
app.run()
