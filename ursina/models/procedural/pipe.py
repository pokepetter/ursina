from ursina import *
from ursina.duplicate import duplicate
from ursina.ursinamath import sample_gradient


class Pipe(Mesh):
    def __init__(self, base_shape=Quad, origin=(0,0), path=((0,0,0),(0,1,0)), thicknesses=((1,1),), color_gradient=None, look_at=True, cap_ends=True, mode='triangle', **kwargs):
        if callable(base_shape):
            base_shape = base_shape()

        self.base_shape = base_shape
        self.origin = origin
        self.path = path
        self.thicknesses = thicknesses
        self.look_at = look_at
        self.cap_ends = cap_ends
        self.mode = mode
        self.color_gradient = color_gradient
        super().__init__(**kwargs)


    def generate(self):
        shape = self.base_shape.vertices
        # make the base shape and rotate it
        b = Entity(position=self.path[0], color=color.lime, scale=self.thicknesses[0], origin=self.origin)
        for p in shape:
            Entity(parent=b, position=Vec3(p), model='cube', scale=(.05, .05, .05), color=color.yellow)

        b.look_at(self.path[1])
        e = duplicate(b)

        verts = []
        self.colors = []

        # cap start
        if self.cap_ends:
            for i in range(len(b.children)):
                verts.append(self.path[0])
                verts.append(b.children[i].world_position)
                if i >= len(b.children)-1:
                    verts.append(b.children[0].world_position)
                else:
                    verts.append(b.children[i+1].world_position)

                if self.color_gradient:
                    self.colors.extend([self.color_gradient[0], ]*3)

        for i in range(1, len(self.path)):
            b.position = self.path[i-1]
            if self.look_at:
                b.look_at(self.path[i])
            e.position = self.path[i]
            if i+1 < len(self.path) and self.look_at:
                e.look_at(self.path[i+1])

            # for debugging sections
            # clone = duplicate(e)
            # clone.color=color.brown
            # clone.scale *= 1.1

            try:
                e.scale = self.thicknesses[i]
                b.scale = self.thicknesses[i-1]
            except:
                pass

            # add sides
            for j in range(len(e.children)):
                n = j+1
                if j == len(e.children)-1:
                    n = 0
                verts.append(e.children[j].world_position)
                verts.append(b.children[n].world_position)
                verts.append(b.children[j].world_position)

                verts.append(e.children[n].world_position)
                verts.append(b.children[n].world_position)
                verts.append(e.children[j].world_position)

                from_color = sample_gradient(self.color_gradient, (i-1)/(len(self.path)-1))
                to_color = sample_gradient(self.color_gradient, (i-0)/(len(self.path)-1))
                if self.color_gradient:
                    self.colors.append(to_color)
                    self.colors.append(from_color)
                    self.colors.append(from_color)
                    self.colors.append(to_color)
                    self.colors.append(from_color)
                    self.colors.append(to_color)

        # cap end
        if self.cap_ends:
            for i in range(len(e.children)):
                if i >= len(e.children)-1:
                    verts.append(e.children[0].world_position)
                else:
                    verts.append(e.children[i+1].world_position)
                verts.append(e.children[i].world_position)
                verts.append(self.path[-1])

                if self.color_gradient:
                    self.colors.extend([self.color_gradient[-1], ]*3)

        self.vertices = verts
        super().generate()
        destroy(b)
        destroy(e)



if __name__ == '__main__':
    app = Ursina()
    # e = Entity(model=Prism(mode='line'))
    path = (Vec3(0,0,0), Vec3(0,1,0), Vec3(0,3,0), Vec3(0,4,0), Vec3(2,5,0))
    thicknesses = ((1,1), (.5,.5), (.75,.75), (.5,.5), (1,1))
    e = Entity(model=Pipe(path=path, thicknesses=thicknesses, color_gradient=[color.black, color.white]))
    # print(e.model.colors)
    print(len(e.model.vertices), len(e.model.colors))
    # e.model.colorize()
    # e2 = duplicate(e)
    # e2.x=2
    # e2.color=color.red

    EditorCamera()
    origin = Entity(model='cube', color=color.magenta)
    origin.scale *= .25
    app.run()
