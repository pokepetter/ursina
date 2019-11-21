from ursina import *
import random


app = Ursina()

color.text_color = color.dark_text

names = ['Amy', 'Ruby', 'Tara', 'Ann', 'Samantha', 'Gary', 'Lee', 'Frank', 'Joe', 'Thomas']

random.seed(0)
data = dict()
for name in names:
    data[name] = random.randint(0, 100)

sliders = list()

for i, (name, value) in enumerate(data.items()):
    e = Button(
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
    e.tooltip.text = value
    e.text_entity.scale *= .4
    e.text_entity.world_y = e.world_y - .2
    e.text_entity.z = -.5
    e.text_entity.world_parent = scene
    e.text_entity.color = e.color.tint(-.5)

    s = ThinSlider(text=name, min=0, max=100, default=value, x=-.65, y=(-i*.04*.75) - .15, step=1, dynamic=True)
    s.scale *= .75
    s.column = e
    sliders.append(s)

    exec(dedent(f'''
        def on_{name}changed():
            sliders[{i}].column.scale_y = sliders[{i}].value/50
            sliders[{i}].column.tooltip.text = str(sliders[{i}].value)
            c = sliders[{i}].column.color
            # sliders[{i}].column.color = color.color(c.h, sliders[{i}].value/100, c.v)

        s.on_value_changed = on_{name}changed
        '''))

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
