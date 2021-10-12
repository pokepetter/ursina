from ursina import *
from copy import copy, deepcopy


def duplicate(entity, copy_children=True, **kwargs): # use a for loop instead of duplicate() if you can.
    if entity.__class__ == Entity:
        e = entity.__class__(entity.add_to_scene_entities)
    else:
        e = entity.__class__()


    if hasattr(entity, 'model') and entity.model:
        e.model = copy(entity.model)


    for name in entity.attributes:
        if name == 'model':
            continue
        elif name == 'collider' and entity.collider and entity.collider.name:
            # TODO: currently only copies colliders set with strings, not custom colliders.
            e.collider = entity.collider.name

        elif name == 'scripts':
            for script in entity.scripts:
                e.add_script(copy(script))

        else:
            if hasattr(entity, name):
                setattr(e, name, getattr(entity, name))

    for c in entity.children:
        clone = duplicate(c, copy_children=False)
        clone.world_parent = e

    if isinstance(e, Audio):
        e.volume = entity.volume
        e.pitch = entity.pitch
        e.balance = entity.balance
        e.loop = entity.loop
        e.loops = entity.loops
        e.autoplay = entity.autoplay

        e.clip = entity.clip


    if hasattr(entity, 'text'):
        e.text = entity.text


    for key, value in kwargs.items():
        setattr(e, key ,value)

    return e


if __name__ == '__main__':
    app = Ursina()

    # quad = Button(parent=scene, model='quad', texture='brick', x=-1, collider='box')
    # sprite = Sprite('brick', x=-2, scale=1.5)
    # circle = Entity(model=Circle(6))
    # rounded_quad = Entity(model=Quad(subdivisions=3, mode='line'), x=1)
    # cone = Entity(model=Cone(), x=3)
    # cone.model.colorize()
    # pipe = Entity(model=Pipe(), x=4)
    # cylinder = Entity(model=Cylinder(), x=5)
    # mesh = Entity(model=Mesh(vertices=((0,0,0), (0,1,0), (-1,1,0))), x=6)
    #
    # for i, e in enumerate((quad, sprite, circle, rounded_quad, sphere, cone, pipe, cylinder, mesh)):
    #     e2 = duplicate(e)
    #     e2.y += 1.5

    e = Button(parent=scene, scale=1, text='yolo')
    # e.c = Entity(parent=e, model='cube', scale=.5, y=.5, color=color.azure)
    e2 = duplicate(e, x=1.25)
    # print(e.text_entity.z, e2.text_entity.z)
    # e2.x +=1.1
    EditorCamera()
    app.run()
