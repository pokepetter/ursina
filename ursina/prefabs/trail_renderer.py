from ursina import *

class TrailRenderer(Entity):
    def __init__(self, target=None,thickness=5,length=6, **kwargs):
        super().__init__()
        self.thickness=thickness
        self.length=length
        self.target = target
        if not target:
            self.target = self
        self.model = Mesh(
            vertices=[self.target.world_position for i in range(self.length)],
            colors=[lerp(color.clear, color.white, i/self.length*2) for i in range(self.length)],
            mode='line',
            thickness=self.thickness,
            static=False,
            
        )



        self._t = 0
        self.update_step = .025
        self.lifetime=0



    def update(self):

        
        self._t += time.dt
        if self._t >= self.update_step and self.lifetime==self.length:
            self._t = 0

            self.model.vertices.pop(0)                
            self.model.vertices.append(self.target.world_position)
            self.model.generate()
        elif self.lifetime < self.length:
            self.model.vertices.pop(0)                
            self.model.vertices.append(self.target.world_position)

            self.lifetime+=1
            


if __name__ == '__main__':
    app = Ursina()
    mouse.visible = False
    player = Entity(model='cube', scale=.1, color=color.orange)
    trail_renderer = TrailRenderer(target=player)

    def update():
        player.position = mouse.position * 10

    app.run()
