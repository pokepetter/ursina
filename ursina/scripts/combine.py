from ursina import *




def combine(entity, analyze=False, auto_destroy=True, ignore=[]):
    verts = list()
    tris = list()
    norms = list()
    uvs = list()
    cols = list()
    to_destroy = list()
    o = 0


    for e in scene.entities:
        if e in ignore:
            continue
            
        if e.has_ancestor(entity) or e == entity:
            if not hasattr(e, 'model') or e.model == None or e.scripts or e.eternal:
                continue
            if not e.model.vertices:
                continue

            if analyze:
                print('combining:', e)

            verts += get_vertices(e, entity)

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
    if analyze:
        render.analyze()
    return entity.model



def get_vertices(entity, relative_to=None):
    if relative_to is None:
        return entity.model.vertices

    vertices = list()
    temp_entity = Entity(parent=entity, ignore=True)

    for v in entity.model.vertices:
        temp_entity.position = v
        vertices.append(temp_entity.get_position(relative_to))

    from ursina import destroy
    destroy(temp_entity)

    return vertices


if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    p = Entity()
    e1 = Entity(parent=p, model='sphere', y=1.5, color=color.pink)
    e2 = Entity(parent=p, model='cube', color=color.yellow, x=1, origin_y=-.5)
    e3 = Entity(parent=e2, model='cube', color=color.yellow, y=2, scale=.5)
    p.combine()
    # p.y=2
    # p.model.save()
    # ursina_mesh_to_obj(p.model, name='combined_model_test', out_path=application.asset_folder)


    EditorCamera()
    app.run()
