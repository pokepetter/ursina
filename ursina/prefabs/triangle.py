from ursina import *


class Triangle(Entity):
    def __init__(self, size=1, color=color.white):
        super().__init__(size=size, color=color)
        self.v1 = Entity(model='quad', scale=(0, 0))
        self.v2 = Entity(model='quad', scale=(0, 0))
        self.v3 = Entity(model='quad', scale=(0, 0))

        self.v1.position = (-0.5 * self.size, -0.5 * self.size, 0)
        self.v2.position = (0.5 * self.size, -0.5 * self.size, 0)
        self.v3.position = (0, 0.5 * self.size, 0)

        self.triangle = Entity(
            model=Mesh(vertices=[self.v1.position, self.v2.position, self.v3.position], mode='triangle'),
            color=self.color)


if __name__ == "__main__":
    app = Ursina()

    Triangle(size=1)

    app.run()
