from ursina import *

class TrailRenderer(Entity):
    def __init__(self, target=None, **kwargs):
        super().__init__()
        self.model = Mesh(
            vertices=[Vec3(0,0,0) for i in range(6)],
            colors=[lerp(color.clear, color.white, i/6*2) for i in range(6)],
            mode='line',
            thickness=5,
            static=False
        )
        self.target = target
        if not target:
            self.target = self

        self._t = 0
        self.update_step = .025


    def update(self):
        self._t += time.dt
        if self._t >= self.update_step:
            self._t = 0
            self.model.vertices.pop(0)
            self.model.vertices.append(self.target.world_position)
            self.model.generate()


if __name__ == '__main__':
    app = Ursina()
    mouse.visible = False
    player = Entity(model='cube', scale=.1, color=color.orange)
    trail_renderer = TrailRenderer(target=player)

    def update():
        player.position = mouse.position * 10

    app.run()
