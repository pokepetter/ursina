from ursina import *
from copy import copy, deepcopy


def duplicate(entity):
    e = entity.__class__(add_to_scene_entities=entity in scene.entities)

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
        clone = duplicate(c)
        clone.parent = e

    if 'Audio' in e.types:
        e.volume = entity.volume
        e.pitch = entity.pitch
        e.balance = entity.balance
        e.loop = entity.loop
        e.loops = entity.loops
        e.autoplay = entity.autoplay

        e.clip = entity.clip


    return e


if __name__ == '__main__':
    app = Ursina()

    quad = Button(parent=scene, model='quad', texture='brick', x=-1, collider='box')
    sprite = Sprite('brick', x=-2, scale=1.5)
    circle = Entity(model=Circle(6))
    rounded_quad = Entity(model=Quad(subdivisions=3, mode='line'), x=1)
    sphere = Entity(model=Sphere(mode='line'), x=2)
    cone = Entity(model=Cone(), x=3)
    cone.model.colorize()
    prismatoid = Entity(model=Prismatoid(), x=4)
    cylinder = Entity(model=Cylinder(), x=5)
    mesh = Entity(model=Mesh(vertices=((0,0,0), (0,1,0), (-1,1,0))), x=6)

    for i, e in enumerate((quad, sprite, circle, rounded_quad, sphere, cone, prismatoid, cylinder, mesh)):
        e2 = duplicate(e)
        e2.y += 1.5

    EditorCamera()
    app.run()
