from mesh import Mesh

def rectangle(rounded_size=0, corner_subdivision=0):
    verts = (
        (-.5, -.5, 0),
        (.5, -.5, 0),
        (.5, .5, 0),
        (-.5, .5, 0)
        )

    return Mesh(verts, type='ngon')


if __name__ == '__main__':
    from ursina import *
    app = ursina()

    e = Entity()
    e.model = rectangle()

    app.run()
