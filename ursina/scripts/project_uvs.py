from ursina import *


def project_uvs(model, aspect_ratio=1):
    uvs = list()
    for v in model.vertices:
        uvs.append(((v[0]+.5) / aspect_ratio, v[1]+.5))

    model.uvs = uvs
    model.generate()




if __name__ == '__main__':
    app = Ursina()

    e = Entity(model='sphere', texture='ursina_logo')
    project_uvs(e.model)
    EditorCamera()

    app.run()
