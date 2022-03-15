from ursina import *

app = Ursina()
points = LoopingList([Draggable(parent=scene, model='circle', scale=.25, x=-4+(i*1)) for i in range(6)])

mover = Entity(model='quad', scale=.3, t=0, color=color.red, position=points[0].position)
mover_2 = Entity(model='quad', scale=1, t=0, color=color.lime, speed=0)

line_renderer = Entity(model=Mesh(vertices=[Vec3(0), Vec3(0)], mode='line', thickness=5), z=.1)
def update():
    line_renderer.model.vertices = [e.position for e in points]
    line_renderer.model.generate()
    mover_2.look_at_2d(mover)
    # mover_2.position += mover_2.up * mover_2.speed * time.dt
    mover_2.position = lerp(mover_2.position, mover.position, time.dt*2)

speed = 10
def play():
    mover.position = points[0].position
    mover_2.position = mover.position

    delay = 0
    for i, e in enumerate(points):
        if i == len(points)-1:
            break

        dist_to_next = distance_2d(points[i].position, points[i+1].position)

        invoke(setattr, mover, 'position', points[i].position, delay=delay/speed)
        mover.animate_position(points[i+1].position, duration=dist_to_next/speed, delay=delay/speed, curve=curve.linear)
        delay += dist_to_next


play_button = Button(text='play', y=-.3, color=color.azure, on_click=play)
play_button.fit_to_text()


app.run()
