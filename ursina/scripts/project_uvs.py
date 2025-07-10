from ursina.vec2 import Vec2
from ursina.vec3 import Vec3


def project_uvs(model, aspect_ratio=1, direction=Vec3.forward, regenerate=False):
    uvs = list()
    if direction == Vec3.forward:
        for v in model.vertices:
            uvs.append(((v[0]+.5) / aspect_ratio, v[1]+.5))

    elif direction == Vec3.down:
        model.uvs = [Vec2((v[0]+.5) / aspect_ratio, v[2]+.5) for v in model.vertices]

    model.uvs = uvs
    if regenerate:
        model.generate()



if __name__ == '__main__':
    from ursina import EditorCamera, Entity, Ursina
    from ursina.scripts.project_uvs import project_uvs
    app = Ursina()

    e = Entity(model='sphere', texture='ursina_logo')
    project_uvs(e.model)
    EditorCamera()

    app.run()
