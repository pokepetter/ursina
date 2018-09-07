from ursina import *


def grid_layout(l, direction=(1,-1), max_x=3, spacing=(.1,.1), origin=(-.5,.5)):
    grid = chunk_list(l, max_x)
    width = 0
    height = 0
    y = 0
    ypos = 0

    for row in grid:
        if y > 0:
            ypos += max([e.scale_y for e in row]) + spacing[1] * direction[1]

        xpos = 0
        for x in range(len(row)):
            if x > 0:
                xpos += row[x-1].scale_x + spacing[0]
            row[x].x = xpos * direction[0]
            row[x].y = ypos * direction[1]

            if xpos > width:
                width = xpos

        y += 1

    # center it
    height = ypos
    for c in l:
        c.x -= (width / 2) + (width * origin[0])
        c.y += height / 2 + (height * -origin[1])


if __name__ == '__main__':
    app = Ursina()

    center = Entity(model='quad', scale=(.1,.1), color=color.red)
    p = Entity()
    for i in range(8):
        b = Button(parent=p, scale=(.5, .5), text=str(i), color=color.tint(color.random_color(),-.6))

    grid_layout(p.children)

    app.run()
