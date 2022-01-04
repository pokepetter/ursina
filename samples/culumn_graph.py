from ursina import *
import random


app = Ursina()

color.text_color = color.dark_text

names = ['Amy', 'Ruby', 'Tara', 'Ann', 'Samantha', 'Gary', 'Lee', 'Frank', 'Joe', 'Thomas']

random.seed(0)
data = {name: random.randint(0, 100) for name in names}
sliders = []

for i, (name, value) in enumerate(data.items()):
    column = Button(
        parent = scene,
        name = name,
        model = 'cube',
        x = i - (len(names)/2),
        scale = (.5, value/50, .5),
        color = color.color(30*i, 1, .7),
        origin_y = -.5,
        text = name,
        tooltip = Tooltip('00') # to ensure uniform with
    )
    column.tooltip.text = value
    column.text_entity.scale *= .4
    column.text_entity.world_y = column.world_y - .2
    column.text_entity.z = -.5
    column.text_entity.world_parent = scene
    column.text_entity.color = column.color.tint(-.5)

    slider = ThinSlider(text=name, min=0, max=100, default=value, x=-.65, y=(-i*.04*.75) - .15, step=1, dynamic=True)
    slider.scale *= .75
    sliders.append(slider)

    def on_slider_changed(slider=slider, column=column):
        column.scale_y = slider.value/50
        column.tooltip.text = str(slider.value)

    slider.on_value_changed = on_slider_changed


randomize_button = Button(position=(-.66,-.45), origin=(-.5,.5), color=color.dark_gray, text='<white>Randomize!', scale=(.25, .05))
randomize_button.scale *= .75

def randomize():
    for s in sliders:
        s.value = random.randint(0,100)
        s.on_value_changed()

randomize_button.on_click = randomize



window.color=color.light_gray.tint(.1)
window.fps_counter.enabled = False
window.exit_button.visible = False
camera.orthographic = True
camera.fov = 8
EditorCamera()

app.run()
