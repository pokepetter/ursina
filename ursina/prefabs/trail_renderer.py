from ursina import *

class TrailRenderer(Entity):
    def __init__(self, thickness=10, color=color.white, end_color=color.clear, length=6, **kwargs):
        super().__init__(**kwargs)
        self.renderer = Entity(
            model = Mesh(
            vertices=[self.world_position for i in range(length)],
            colors=[lerp(end_color, color, i/length*2) for i in range(length)],
            mode='line',
            thickness=thickness,
            static=False
            )
        )
        self._t = 0
        self.update_step = .025


    def update(self):
        self._t += time.dt
        if self._t >= self.update_step:
            self._t = 0
            self.renderer.model.vertices.pop(0)
            self.renderer.model.vertices.append(self.world_position)
            self.renderer.model.generate()

    def on_destroy(self):
        destroy(self.renderer)



if __name__ == '__main__':
    app = Ursina()
    window.color = color.black
    mouse.visible = False
    player = Entity()
    player.graphics = Entity(parent=player, scale=.1, model='circle')
    trail_renderer = TrailRenderer(parent=player, thickness=100, color=color.yellow, length=6)

    pivot = Entity(parent=player)
    trail_renderer = TrailRenderer(parent=pivot, x=.1, thickness=20, color=color.orange)
    trail_renderer = TrailRenderer(parent=pivot, y=1, thickness=20, color=color.orange)
    trail_renderer = TrailRenderer(parent=pivot, thickness=2, color=color.orange, alpha=.5, position=(.4,.8))
    trail_renderer = TrailRenderer(parent=pivot, thickness=2, color=color.orange, alpha=.5, position=(-.5,.7))

    def update():
        player.position = lerp(player.position, mouse.position*10, time.dt*4)

        if pivot:
            pivot.rotation_z -= 3
            pivot.rotation_x -= 2

    def input(key):
        if key == 'space':
            destroy(pivot)


    app.run()
