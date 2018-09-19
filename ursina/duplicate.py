from ursina import *

def duplicate(entity):
    e = entity.__class__()

    if entity.model:
        try:
            e.model = eval(entity.model.constructor) # procedural mesh
        except:
            e.model = entity.model.constructor # loaded mesh

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

    return e


if __name__ == '__main__':
    app = Ursina()
    e = Entity(model=Cone())
    sphere = Entity(parent=e, model='cube', y=1)
    # e = Entity(model='cube')
    e2 = duplicate(e)
    e2.x = 1
    app.run()
