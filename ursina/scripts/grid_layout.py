from ursina import *


def grid_layout(l, max_x=8, max_y=8, spacing=(0,0,0), origin=(-.5,.5,0), offset=(0,0,0)):
    if len(origin) == 2:
        origin += (0,)
    if not isinstance(l, list):
        print('error: grid_layout input must be a list or tuple, not', l.__class__.__name__)
        return
    x, y, z = 0, 0, 0

    slices = chunk_list(l, max_x * max_y)
    for s in slices:
        rows = [e for e in chunk_list(s, max_x)]
        height = sum([max([e.bounds[1] for e in r]) for r in rows])
        y = 0
        for row in rows:
            x = 0
            width = sum([e.bounds[0] for e in row])
            for e in row:
                e.position = (
                    x + l[0].bounds[0]/2 - width/2 - (width/2 * origin[0]*2),
                    y + l[0].bounds[1]/2 - height/2 - (height/2 * origin[1]*2),
                    z + l[0].bounds[2]/2)

                x += e.bounds[0]
            y += max([e.bounds[1] for e in row]) + spacing[1]
        z += max([e.bounds[2] for e in s]) + spacing[2]

    for e in l:
        e.z -= z/2 - (z/2 * origin[2]*2)



if __name__ == '__main__':
    app = Ursina()

    center = Entity(model='quad', scale=.1, color=color.red)
    p = Entity()
    for i in range(32):
        b = Button(parent=p, model='cube', scale=.5, scale_x=1, text=str(i), color=color.tint(color.random_color(),-.6))

    t = time.time()
    grid_layout(p.children, max_x=4, max_y=3, origin=(-.5, .5))
    center = Entity(parent=camera.ui, model=Circle(), scale=.005, color=color.lime)
    EditorCamera()
    print(time.time() - t)

    app.run()
