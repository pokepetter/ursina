from ursina import *
from ursina import color
import math
from ursina.vec3 import Vec3
# import numpy as np


def get_world_normals(model):
    import numpy as np
    normals = [np.array((n[0], n[2], n[1])) for n in model.normals]
    object_matrix = model.getNetTransform().getMat()
    normals = [object_matrix.xformVec(Vec3(*n)) for n in normals]
    normals = [Vec3(n[0], n[2], n[1]).normalized() for n in normals]
    return normals


def colorize(model, left=color.white, right=color.blue, down=color.red, up=color.green, back=color.white, forward=color.white, smooth=True, world_space=True):

    if not model.normals:
        print('generating normals for', model)
        model.generate_normals(smooth=smooth)

    if world_space:
        normals = get_world_normals(model)
    else:
        normals = model.normals

    cols = list()
    prev_col = color.white
    for n in normals:
        # c = color.rgb((n[0]/2)+.5, (n[1]/2)+.5, (n[2]/2)+.5)
        c = lerp(down, up, (n[1]/2 +.5))

        if n[0] < 0:
            c = lerp(c, left, -(n[0]/2))
        else:
            c = lerp(c, right, (n[0]/2))

        if n[2] < 0:
            c = lerp(c, back, -(n[2]/2))
        else:
            c = lerp(c, forward, (n[2]/2))

        has_nan = False
        for e in c:
            if math.isnan(e):
                has_nan = True
                break

        if not has_nan:
            prev_col = c
            cols.append(c)
        else:
            cols.append(prev_col)


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
    # colorize(e.model, smooth=False)
    # print(e.getNetTransform().getMat())
    # # e2.rotation_x = 180
    import random
    for i in range(10):
        e = Entity(model='sphere')
        e.position = (random.uniform(-3,3),random.uniform(-3,3),random.uniform(-3,3))
        e.rotation = (random.uniform(0,360),random.uniform(0,360),random.uniform(0,360))
        e.scale = random.uniform(1,3)
        # e.look_at(d)
        # e.x = i
        e.model.colorize(smooth=False)
            # color.black,
            # color.black,
            # color.black,
            # color.white,
            # color.black,
            # color.black,
            # smooth=False)


    # e = Entity(model='sphere', z=0)
    # print(e.getNetTransform().getMat())
    # print(e.getMat())

    Sky(color=color.gray)
    EditorCamera()
    app.run()
