from ursina import *


def grid_layout(l, direction=(1,1,1), max_x=8, max_y=8, spacing=(0,0,0), origin=(-.5,.5,0)):
    e_size = [s[0] * s[1] for s in zip(l[0].bounds, l[0].scale)]

    for i, e in enumerate(l):
        z = i // (max_x * max_y)
        rest = i - z * (max_x * max_y)
        y = rest // max_x
        x = rest - (y * max_x)

        e.position = (
            x * (e_size[0]+spacing[0]) * direction[0],
            y * (e_size[1]+spacing[1]) * direction[1],
            z * (e_size[2]+spacing[2]) * direction[2]
            )

    # center it
    width = max(len(l), max_x) * (e_size[0]+spacing[0])
    height = max(len(l), max_x*max_y) * (e_size[1]+spacing[1])
    for c in l:
        c.x -= (width / 2) + (width * origin[0])
        c.y += height / 2 + (height * -origin[1])


if __name__ == '__main__':
    app = Ursina()

    center = Entity(model='quad', scale=(.1,.1), color=color.red)
    p = Entity()
    for i in range(16):
        b = Button(parent=p, model='cube', scale=(.5, .5, .5), text=str(i), color=color.tint(color.random_color(),-.6))

    t = time.time()
    grid_layout(p.children, max_x=3, max_y=3)
    EditorCamera()
    print(time.time() - t)

    app.run()
