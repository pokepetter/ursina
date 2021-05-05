from ursina import *

class TrailRenderer(Entity):
    def __init__(self, color1, color2, thickness=5, target=None, length=5, destroy_on_stop=False, **kwargs):
        super().__init__()
        self.target = target
        self.model = Mesh(
            vertices=[(target.world_position) for i in range(length)],
            colors=[lerp(color1, color2, i/length) for i in range(10)],
            mode='line',
            thickness=thickness,
            static=False
        )
        if not target:
            target=self

        self._t = 0
        self.update_step = .01

        for key, value in kwargs.items():
             setattr(self, key ,value)


    def update(self):
        self._t += time.dt
        if self._t >= self.update_step:
            self._t = 0
            self.model.vertices.pop(0)
            self.model.vertices.append(self.target.world_position)
            self.model.generate()
        if all(elem == self.model.vertices[0] for elem in self.model.vertices) and destroy_on_stop:
          destroy(self)


if __name__ == '__main__':
    app = Ursina()
    mouse.visible = False
    player = Entity(model='cube', scale=.1, color=color.orange)
    trail_renderer = TrailRenderer(target=player)

    def update():
        player.position = mouse.position * 10

    app.run()
