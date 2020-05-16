from ursina import *

app = Ursina()


# options_menu = Entity(parent=camera.ui, model='quad', color=color.dark_gray, collider='box', z=-1, enabled=False)

main_menu = Entity(parent=camera.ui)
options_menu = Entity(parent=camera.ui, enabled=False)

button_size = (.25, .075)
buttons = [
    Button('resume', scale=button_size),
    Button('new game', scale=button_size),
    Button('load game', scale=button_size),
    Button('options', scale=button_size, on_click=Func(setattr, options_menu, 'enabled', True)),
    Button('quit', scale=button_size, on_click=Sequence(Wait(.01), Func(sys.exit))),
]
for i, b in enumerate(buttons):
    b.parent = main_menu
    # b.scale = (.25, .1)
    b.y = .05 + (-i * .1)


scale = 1
def set_text_scale(multiplier):
    global scale
    scale *= multiplier
    if scale < .5 or scale > 2:
        return  # limit

    for t in [e for e in scene.entities if isinstance(e, Text)]:
        t.scale *= multiplier


WindowPanel(
    parent=options_menu,
    title='Options',
    y=.35,
    content=(
        Space(1),
        Text('Text size:'),
        Button('-', on_click=Func(set_text_scale, 1/1.1)),
        Button('+', on_click=Func(set_text_scale, 1.1)),
        # Text('Age:'),
        # InputField(name='age_field'),
        # Space(height=1),
        # Text('Send:'),
        Button(text='Apply', color=color.green),
        Button(text='Reset'),
        Button(text='Back'),
        # ButtonGroup(('test', 'eslk', 'skffk'))
        ),
    # on_enable = Func(print, 'enabled')
    )
options_menu.on_enable = Func(setattr, main_menu, 'enabled', False)


app.run()
