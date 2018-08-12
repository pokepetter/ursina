from ursina import *


class TransformField(Button):

    def __init__(self):
        super().__init__()
        self.name = 'transform_field'

        self.transform_type = 0
        self.axis = Vec3(1, 0, 0)
        self.target_entity = None
        self.move_entity = None


    @property
    def direction(self, value):
        return Vec3(value[0], value[1], value[2])


    def input(self, key):
        if self.hovered and key == 'left mouse down':
            self.move_entity = True

        if key == 'left mouse up':
            self.move_entity = False

            if self.hovered and mouse.delta_drag == (0,0):
                print('enter number')


    def update(self):
        if self.move_entity:
            if self.transform_type == 0:
                self.target_entity.position += self.axis * mouse.velocity[0]
            elif self.transform_type == 1:
                self.target_entity.rotation += self.axis * mouse.velocity[0]
            elif self.transform_type == 2:
                self.target_entity.scale += self.axis * mouse.velocity[0]


if __name__ == '__main__':
    app = Ursina()
    tf = TransformField()
    tf.target_entity = Entity('target')
    app.run()
