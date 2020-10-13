from ursina import *

app = Ursina()

title = Text('''position, rotation, scale and parenting demo''', position=(-.85, .475), scale=1.5)

entity = Entity(model='cube', texture='white_cube')
child = Entity(parent=entity, x=1, model='cube', scale=.5, texture='white_cube', color=color.azure)
spacing = .04
ui_parent = Entity(parent=camera.ui, scale=.8, x=-.85)

for y, e in enumerate((entity, child)):
    for i, name in enumerate(('x', 'y', 'z')):
        slider = Slider(-1, 1, default=getattr(e, name), text=name, dynamic=True, position=(.1, .4-(i*spacing)-y*.5), parent=ui_parent)
        def on_slider_changed(e=e, slider=slider, attr_name=name):
            setattr(e, attr_name, slider.value)
        slider.on_value_changed = on_slider_changed

        name = 'rotation_' + name
        slider = Slider(0, 360, default=getattr(e, name), text=name, dynamic=True, position=(.1, .4-(i*spacing)-(spacing*3)-y*.5), parent=ui_parent)
        def on_slider_changed(e=e, slider=slider, attr_name=name):
            setattr(e, attr_name, slider.value)
        slider.on_value_changed = on_slider_changed

        name = 'scale_' + name.split('_')[1]
        slider = Slider(.1, 3, default=getattr(e, name), text=name, dynamic=True, position=(.1, .4-(i*spacing)-(spacing*6)-y*.5), parent=ui_parent)
        def on_slider_changed(e=e, slider=slider, attr_name=name):
            setattr(e, attr_name, slider.value)
        slider.on_value_changed = on_slider_changed

t = Text('''white cube:''', position=(0, .4+spacing*1.5), parent=ui_parent)
t.create_background(.025, 0.0125)
t = Text('''blue cube (parented to the white cube):''', position=(0, -spacing), parent=ui_parent)
t.create_background(.025, 0.0125)

EditorCamera()

app.run()
