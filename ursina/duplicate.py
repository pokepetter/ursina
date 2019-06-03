from ursina import *

def duplicate(entity):
    e = entity.__class__()

    if hasattr(entity, 'model') and entity.model:
        try:
            e.model = eval(entity.model.recipe) # procedural mesh
        except:
            try:
                e.model = entity.model.recipe # loaded mesh
            except:
                print(f'error: model: {entity.model} has no recipe', entity.model.recipe)

    for name in entity.attributes:
        if name == 'model':
            continue
        elif name == 'scripts':
            pass
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
    # e = Entity(model='quad')
    # e = Entity(model=Circle(6))
    # e = Entity(model=Quad(subdivisions=3, mode='lines'))
    # e = Entity(model=Sphere(mode='lines'))
    # e = Entity(model=Cone())
    # e = Entity(model=Prismatoid())
    # e = Entity(model=Cylinder())
    e = Entity(model=Mesh(vertices=((0,0,0), (0,1,0), (1,1,0))))
    print(e.model.recipe)
    # test that children are duplicated
    # sphere = Entity(parent=e, model='cube', y=1)
    e2 = duplicate(e)
    e2.x = 1
    e2.color = color.red
    EditorCamera()
    app.run()
