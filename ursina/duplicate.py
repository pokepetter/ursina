from ursina import Entity, Audio
from copy import copy


def duplicate(entity, copy_children=True, *args, **kwargs): # use a for loop instead of duplicate() if you can.
    if entity.__class__ == Entity:
        e = entity.__class__(entity.add_to_scene_entities, *args, **kwargs)
    else:
        e = entity.__class__(*args, **kwargs)


    if hasattr(entity, 'model') and entity.model:
        e.model = copy(entity.model)


    for name in entity.attributes:
        if name == 'model':
            continue
        if name == 'collider' and entity.collider and entity.collider.name:
            # TODO: currently only copies colliders set with strings, not custom colliders.
            e.collider = entity.collider.name
            continue
        if name == 'scripts':
            for script in entity.scripts:
                e.add_script(copy(script))
            continue

        else:
            if hasattr(entity, name):
                setattr(e, name, getattr(entity, name))

    e.shader_input = entity.shader_input

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
    from ursina import *
    from ursina import Ursina, Button, scene, EditorCamera
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

    new_parent = Entity(scale=1)
    from ursina.shaders import matcap_shader, triplanar_shader
    e = Button(parent=scene, scale=2, text='test', texture='shore', texture_scale=Vec2(2), color=color.gray)
    e.c = Entity(parent=e, model='icosphere', scale=.5, y=.5, shader=matcap_shader, texture='matcap_4')
    e.c2 = Entity(parent=e.c, model='cube', scale=.5, y=.5, x=1, color=color.green, shader=triplanar_shader, texture='grass')

    e2 = duplicate(e, x=2.25, parent=new_parent)
    # print(e.text_entity.z, e2.text_entity.z)
    # e2.x +=1.1
    EditorCamera()
    app.run()
