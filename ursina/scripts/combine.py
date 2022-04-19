from ursina import *


def combine(combine_parent, analyze=False, auto_destroy=True, ignore=[]):
    verts = []
    tris = []
    norms = []
    uvs = []
    cols = []
    to_destroy = []
    o = 0

    for e in scene.entities:
        if e in ignore:
            continue

        if e.has_ancestor(combine_parent) or e == combine_parent:
            if not hasattr(e, 'model') or e.model == None or e.scripts or e.eternal:
                continue
            if not hasattr(e.model, 'vertices') or not e.model.vertices:
                e.model = load_model(e.model.name, use_deepcopy=True)
                e.origin = e.origin
            if not e.model:
                continue

            if analyze:
                print('combining:', e)

            vertex_to_world_matrix = e.model.getTransform(combine_parent).getMat()
            verts += [vertex_to_world_matrix.xformPoint(v) for v in e.model.vertices]

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
                cols.extend([Color(*vcol) * e.color for vcol in e.model.colors])
            else:
                cols.extend((e.color, ) * len(e.model.vertices))


            if auto_destroy and e != combine_parent:
                to_destroy.append(e)

    if auto_destroy:
        from ursina import destroy
        [destroy(e) for e in to_destroy]

    combine_parent.model = Mesh(vertices=verts, triangles=tris, normals=norms, uvs=uvs, colors=cols, mode='triangle')
    print('combined')
    # entity.model = Mesh(vertices=verts,  mode='triangle')
    # entity.flatten_strong()
    if analyze:
        render.analyze()
    return combine_parent.model




if __name__ == '__main__':
    from ursina import *
    app = Ursina()


    p = Entity()
    e1 = Entity(parent=p, model='sphere', y=1.5, color=color.pink)
    e2 = Entity(parent=p, model='cube', color=color.yellow, x=1, origin_y=-.5)
    e3 = Entity(parent=e2, model='cube', color=color.yellow, y=2, scale=.5)

    def input(key):
        if key == 'space':
            from time import perf_counter
            t = perf_counter()
            p.combine()
            print('combined in:', perf_counter() - t)

    # p.y=2
    # p.model.save()
    # ursina_mesh_to_obj(p.model, name='combined_model_test', out_path=application.asset_folder)


    EditorCamera()
    app.run()
