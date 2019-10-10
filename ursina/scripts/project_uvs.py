from ursina import *


def project_uvs(model, aspect_ratio=1, direction='forward', regenerate=False):
    uvs = list()
    if direction == 'forward':
        for v in model.vertices:
            uvs.append(((v[0]+.5) / aspect_ratio, v[1]+.5))

    elif direction == 'down':
        for v in model.vertices:
            uvs.append(((v[0]+.5) / aspect_ratio, v[2]+.5))


    model.uvs = uvs

    if regenerate:
        model.generate()




if __name__ == '__main__':
    app = Ursina()

    e = Entity(model='sphere', texture='ursina_logo')
    project_uvs(e.model)
    EditorCamera()

    app.run()
