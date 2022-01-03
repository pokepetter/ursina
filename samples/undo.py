from ursina import *




app = Ursina()

window.color = color._16
cursor = Entity(parent=camera.ui, model=Circle(12), color=color.azure, scale=.05, y=.1)
text = Text(parent=cursor, text='x', z=-1, world_scale=25, y=1.25, origin=(0,0))
mesh = Entity(parent=camera.ui, model=Mesh(mode='point', thickness=10), color=color.white).model
# undo_cache = [color.random_color() for e in range(1)]
undo_cache = [color.random_color()]
undo_index = 0
# undo_index = len(undo_cache)-1
help_text = Text(text='undo example\n\nspace: record action\na: undo\nd: redo', origin=(-.5,.5), position=window.top_left*.95)


def visualize_undo_cache():
    global mesh, cursor, undo_index, undo_cache, text
    mesh.vertices = [Vec3(i/10,0,0) for i in range(len(undo_cache))]
    mesh.colors = list(undo_cache)
    mesh.generate()
    cursor.x = undo_index / 10
    cursor.color = undo_cache[undo_index]
    text.text = undo_index

visualize_undo_cache()



def input(key):
    global undo_cache, undo_index

    if key in ['a', 'z']:
        undo_index -= 1
        undo_index = clamp(undo_index, 0, len(undo_cache)-1)

    if key in ['d', 'y']:
        undo_index += 1
        undo_index = clamp(undo_index, 0, len(undo_cache)-1)

    if key == 'space':
        undo_index += 1
        undo_cache = undo_cache[:undo_index]
        undo_cache.append(color.random_color())


    # undo_index = clamp(undo_index, 0, len(undo_cache)-1)
    visualize_undo_cache()


app.run()
