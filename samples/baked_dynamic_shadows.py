from ursina import *

app = Ursina()
Plane(5, color=color.gray)

class CircularArray(Entity):
    def __init__(self, prefab, amount=5, offset=1, **kwargs):
        super().__init__()

        for key, value in kwargs.items():
            setattr(self, key, value)
        self.prefab = prefab
        self.amount = amount
        self.offset = offset
        self.generate()

    def generate(self):
        for c in self.children:
            destroy(c)

        origin = Entity()
        for i in range(self.amount):
            instance = eval(self.prefab.__name__ + '()')
            instance.parent = origin
            origin.rotation_y = i * 360 / self.amount
            instance.z = self.offset
            # instance.color = color.random_color()
            instance.world_parent = self

        destroy(origin)


class MyPrefab(Entity):
    def __init__(self):
        super().__init__()
        self.model = 'cube'
        self.scale *= .5

ca = CircularArray(prefab=MyPrefab)
b = Button(
    text='+',
    circ_array = ca,
    on_click='''
        self.circ_array.amount += 1
        self.circ_array.generate()
        '''
    )
b.scale *= .05

camera.add_script('editor_camera')




app.run()
