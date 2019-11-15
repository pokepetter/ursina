from ursina import *

def combine(entity, analyze=False, auto_destroy=True):
    verts = list()
    tris = list()
    norms = list()
    uvs = list()
    cols = list()
    to_destroy = list()
    o = 0


    for e in scene.entities:
        if e.has_ancestor(entity) or e == entity:
            if not hasattr(e, 'model') or e.model == None or e.scripts or e.eternal:
                continue
            if not e.model.vertices:
                continue

            print('combining:', e)
            verts += e.get_vertices(entity)

            if not e.model.triangles:
                new_tris = [i for i in range(len(e.model.vertices))]

            else:
                new_tris = list()
                for t in e.model.triangles:
                    if isinstance(t, int):
                        new_tris.append(t)
                    elif len(t) == 3:
                        new_tris.extend(t)
                    elif len(t) == 4: # turn quad into tris
                        new_tris.extend([t[0], t[1], t[2], t[2], t[3], t[0]])

            new_tris = [t+o for t in new_tris]
            new_tris = [(new_tris[i], new_tris[i+1], new_tris[i+2]) for i in range(0, len(new_tris), 3)]

            o += len(e.model.vertices)
            tris += new_tris

            # if e.model.normals:
            #     norms += e.model.normals

            if e.model.uvs:
                uvs += e.model.uvs

            if e.model.colors: # if has vertex colors
                cols.extend(e.model.colors)
            else:
                cols.extend((e.color, ) * len(e.model.vertices))


            if auto_destroy and e != entity:
                to_destroy.append(e)

    if auto_destroy:
        from ursina import destroy
        [destroy(e) for e in to_destroy]

    entity.model = Mesh(vertices=verts, triangles=tris, normals=norms, uvs=uvs, colors=cols, mode='triangle')
    print('combined')
    # entity.model = Mesh(vertices=verts,  mode='triangle')
    # entity.flatten_strong()
    # if analyze:
    #     render.analyze()
    return entity.model

if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    p = Entity()
    e1 = Entity(parent=p, model='sphere', y=1.5, color=color.pink)
    e2 = Entity(parent=p, model='cube', color=color.yellow, x=1, origin_y=-.5)
    # e2.model.generate_normals()
    # e2.model.colorize()
    e3 = Entity(parent=e2, model='cube', color=color.yellow, y=2, scale=.5)
    p.combine()
    # print(p.model.normals)
    p.model.colorize()
    # from ursina.models.procedural.cube import Plane
    # e = Entity()
    #
    # w,h,d = 3,3,3
    # front =  Entity(parent=e, model=Plane((w,h)), z=-.5, rotation_x=-90, name='front')
    # back =   Entity(parent=e, model=Plane((w,h)), z=.5, rotation_x=90, name='back')
    # top =    Entity(parent=e, model=Plane((w,d)), y=.5, name='top')
    # bottom = Entity(parent=e, model=Plane((w,d)), y=-.5, rotation_x=-180, name='bottom')
    # right =  Entity(parent=e, model=Plane((d,h)), x=.5, rotation_z=90, name='right')
    # left =   Entity(parent=e, model=Plane((d,h)), x=-.5, rotation_z=-90, name='left')

    # p.model = combine(e)
    # destroy(e)
    # p.y=2
    # p.model.save()
    # ursina_mesh_to_obj(p.model, name='combined_model_test', out_path=application.asset_folder)


    EditorCamera()
    app.run()
