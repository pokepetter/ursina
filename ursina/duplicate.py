from ursina import *

def duplicate(entity):
    e = entity.__class__()

    if hasattr(entity, 'model') and entity.model:
        recipe = entity.model.recipe

        if not('(') in recipe:
            e.model = recipe # loaded mesh
        else:
            e.model = eval(recipe) # procedural mesh


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
    quad = Entity(model='quad')
    circle = Entity(model=Circle(6))
    rounded_quad = Entity(model=Quad(subdivisions=3, mode='line'), x=1)
    sphere = Entity(model=Sphere(mode='line'), x=2)
    cone = Entity(model=Cone(), x=3)
    cone.model.colorize()
    prismatoid = Entity(model=Prismatoid(), x=4)
    cylinder = Entity(model=Cylinder(), x=5)
    mesh = Entity(model=Mesh(vertices=((0,0,0), (0,1,0), (-1,1,0))), x=6)

    names = ('quad', 'circle', 'rounded_quad', 'sphere', 'cone', 'prismatoid', 'cylinder', 'mesh')
    for i, e in enumerate((quad, circle, rounded_quad, sphere, cone, prismatoid, cylinder, mesh)):
        print(names[i], ':', e.model.recipe)
        print()
        print()
        e2 = duplicate(e)
        e2.y += 1.5
        
    EditorCamera()
    app.run()
