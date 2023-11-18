from ursina import *


def combine(combine_parent, analyze=False, auto_destroy=True, ignore=[], ignore_disabled=True):
    verts = []
    tris = []
    norms = []
    uvs = []
    cols = []
    to_destroy = []
    o = 0
    original_texture = combine_parent.texture

    for e in scene.entities:
        if e in ignore:
            continue

        if ignore_disabled and not e.enabled:
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
            verts += [Vec3(*vertex_to_world_matrix.xformPoint(v)) for v in e.model.vertices]

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
            new_tris = [(new_tris[i], new_tris[i+1], new_tris[i+2]) for i in range(0, len(new_tris)-1, 3)]

            o += len(e.model.vertices)
            tris += new_tris

            # if e.model.normals:
            #     norms += e.model.normals

            if e.model.uvs:
                uvs.extend([(uv * e.texture_scale) + e.texture_offset for uv in e.model.uvs])
            else:
                uvs.extend([(0,0) for e in e.model.vertices])

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
    combine_parent.texture = original_texture
    # print('combined')
    # entity.model = Mesh(vertices=verts,  mode='triangle')
    # entity.flatten_strong()
    if analyze:
        render.analyze()
    return combine_parent.model




if __name__ == '__main__':
    from ursina import *
    from ursina.mesh_exporter import ursinamesh_to_obj
    app = Ursina()


    p = Entity(texture='brick')
    e1 = Entity(parent=p, model='sphere', y=1.5, color=color.pink)
    e2 = Entity(parent=p, model='cube', color=color.yellow, x=1, origin_y=-.5, texture='brick')
    e3 = Entity(parent=e2, model='cube', color=color.yellow, y=2, scale=.5, texture='brick', texture_scale=Vec2(3,3), texture_offset=(.1,.1))

    def input(key):
        if key == 'space':
            from time import perf_counter
            t = perf_counter()
            p.combine()
            p.texture='brick'
            print('combined in:', perf_counter() - t)

    p.combine()
    # p.y=2
    # p.model.save()
    # ursinamesh_to_obj(p.model, name='combined_model_test', out_path=application.asset_folder)
    print(p.model.vertices[0].__class__)

    EditorCamera()
    app.run()
