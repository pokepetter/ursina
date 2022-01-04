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


def colorize(model, left=color.white, right=color.blue, down=color.red, up=color.green, back=color.white, forward=color.white, smooth=True, world_space=True, strength=1):

    if not model.normals:
        print('generating normals for', model)
        model.generate_normals(smooth=smooth)

    normals = get_world_normals(model) if world_space else model.normals
    cols = []
    prev_col = color.white
    for n in normals:
        c = lerp(down, up, ((n[1]*strength) +.5))

        if n[0] < 0:
            c = lerp(c, left, -(n[0]*strength))
        else:
            c = lerp(c, right, (n[0]*strength))

        if n[2] < 0:
            c = lerp(c, back, -(n[2]*strength))
        else:
            c = lerp(c, forward, (n[2]*strength))

        has_nan = any(math.isnan(e) for e in c)
        if not has_nan:
            prev_col = c
            cols.append(c)
        else:
            cols.append(prev_col)


    model.colors = cols
    model.generate()


if __name__ == '__main__':
    app = Ursina()
    import random
    for _ in range(10):
        e = Entity(model=load_model('sphere', path=application.internal_models_compressed_folder, use_deepcopy=True))
        e.position = (random.uniform(-3,3),random.uniform(-3,3),random.uniform(-3,3))
        e.rotation = (random.uniform(0,360),random.uniform(0,360),random.uniform(0,360))
        e.scale = random.uniform(1,3)
        e.model.colorize(smooth=False, world_space=True, strength=.5)


    Sky(color=color.gray)
    EditorCamera()
    app.run()
