from ursina import *


def grid_layout(l, max_x=8, spacing=(0,0), origin=(-.5,.5), offset=(0,0)):
    if not isinstance(l, list | tuple):
        print('error: grid_layout input must be a list or tuple, not', l.__class__.__name__)
        return

    spacing = Vec2(*spacing)
    origin = Vec2(*origin)
    offset = Vec2(*offset)

    dimensions = l[0].bounds.size
    direction = [-e*2 for e in origin]
    direction = Vec2(*[1 if e == 0 else e for e in direction])

    chunked_list = list(chunk_list(l, max_x))

    if origin.y != 0:
        for y, row in enumerate(chunked_list):
            for x, item in enumerate(row):
                item.y = ((y * (dimensions.y + spacing.y)) * direction.y) + (dimensions.y/2 * direction.y) + offset.y
    else:   # center vertically
        total_height = len(chunked_list) * dimensions.y + (len(chunked_list) - 1) * spacing.y
        start_y = -(total_height / 2) + offset.y
        for y, row in enumerate(chunked_list):
            for x, item in enumerate(row):
                item.y = start_y + y * (dimensions.y + spacing.y) + (dimensions.y / 2)

    if origin.x != 0:
        for y, row in enumerate(chunked_list):
            for x, item in enumerate(row):
                item.x = ((x * (dimensions.x + spacing.x)) * direction.x) + (dimensions.x/2 * direction.x) + offset.x

    else:   # center horizontally
        for y, row in enumerate(chunked_list):
            row_width = len(row) * (dimensions.x + spacing.x) - spacing.x
            start_x = -(row_width / 2) + offset.x
            for x, item in enumerate(row):
                item.x = start_x + x * (dimensions.x + spacing.x) + (dimensions.x / 2)


if __name__ == '__main__':
    app = Ursina()

    center = Entity(model='quad', scale=.025, color=color.red, always_on_top=True)
    p = Entity()
    for i in range(13):
        b = Button(parent=p, model='quad', scale=Vec2(.2,.1), text=str(i), color=color.tint(color.random_color(),-.6))
        b.text_entity.scale=1
    t = time.time()
    grid_layout(p.children, origin=(0,.5), spacing=(.1,.1))
    center = Entity(parent=camera.ui, model=Circle(), scale=.005, color=color.lime)
    EditorCamera()
    print(time.time() - t)

    # test
    for e in [(-.5,.5), (0,.5), (.5,.5), (-.5,0), (0,0), (.5,0), (-.5,-.5), (0,-.5), (.5,-.5)]:
        Button(text='*', model='quad', text_origin=e, scale=.095, origin=(-.5,.5), position = window.top_left + Vec2(*e)*.2 + Vec2(.1,-.1), tooltip=Tooltip(str(e)),
            on_click=Func(grid_layout, p.children, max_x=4, origin=e, spacing=(.05,.05))
        )



    app.run()
