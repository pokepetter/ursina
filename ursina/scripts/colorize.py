from ursina import *
from ursina import color



def colorize(model, left=color.white, right=color.blue, down=color.red, up=color.green, back=color.white, forward=color.white):
    if model.normals == None:
        model.generate_normals()

    cols = list()
    for i, n in enumerate(model.normals):
        c = color.rgb((n[0]/2)+.5, (n[1]/2)+.5, (n[2]/2)+.5)
        c = lerp(up, down, (n[1]/2 +.5))

        if n[0] < 0:
            c = lerp(c, right, -(n[0]/2))
        else:
            c = lerp(c, left, (n[0]/2))
        c = (c[0], c[1], c[2], c[3])
        cols.append(c)

    model.colors = cols
    model.generate()
    # return model
    # print('--------------')
# m.setMaterialOff()
# from panda3d.core import Material
# material = Material()
# print(material.getShininess())
# print(material.getMetallic())
# material.setMetallic(128)
# material.setShininess(128)
# m.setMaterial(material)
if __name__ == '__main__':
    app = Ursina()
    e = Entity(model='sphere')
    colorize(e.model)
    # e.shader = 'shader_normals'
    # # print(e.shader.get_text())
    EditorCamera()
    app.run()
