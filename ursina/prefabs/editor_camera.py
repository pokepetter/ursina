from ursina import *

class EditorCamera(Entity):

    def __init__(self, **kwargs):
        super().__init__(name='editor_camera', eternal=True)

        self.pivot = Entity(name='pivot', eternal=True, model='cube', color=color.green, scale=(.05,.05,.05))
        camera.world_parent = self.pivot

        self.rotation_speed = 100
        self.pan_speed = (4, 4)
        self.move_speed = 1
        self.zoom_speed = 20

        for key, value in kwargs.items():
            setattr(self, key, value)


    def input(self, key):
        if key == '+':
            camera.fov += 1
            printvar(camera.fov)
        elif key == '-':
            camera.fov -= 1
            printvar(camera.fov)

        if key == 'p':
            camera.orthographic = not camera.orthographic


        # zooming, don't zoom if hovering an editor panel
        if (mouse.left or mouse.right or mouse.middle
        and mouse.hovered_entity
        and hasattr(mouse.hovered_entity, 'is_editor')
        and mouse.hovered_entity.is_editor):     # hovering editor panel
            pass
        else:
            if key == 'scroll up':
                camera.z += self.zoom_speed
            if key == 'scroll down':
                camera.z -= self.zoom_speed



    def update(self):
        camera.look_at(self.pivot)

        if mouse.right:
            self.pivot.rotation_x -= mouse.velocity[1] * self.rotation_speed
            self.pivot.rotation_y += mouse.velocity[0] * self.rotation_speed

            self.pivot.position += camera.right * held_keys['d'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt']))
            self.pivot.position += camera.left * held_keys['a'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt']))
            self.pivot.position += camera.forward * held_keys['w'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt']))
            self.pivot.position += camera.back * held_keys['s'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt']))
            self.pivot.position += camera.up * held_keys['e'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt']))
            self.pivot.position += camera.down * held_keys['q'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt']))


        if mouse.middle:
            self.pivot.position -= camera.right * mouse.velocity[0] * self.pan_speed[0]
            self.pivot.position -= camera.up * mouse.velocity[1] * self.pan_speed[1]



if __name__ == '__main__':
    app = Ursina()
    '''
    Simple camera for debugging.
    Hold right click and move the mouse to rotate around point.
    '''

    sky = Sky()
    e = Entity(model='cube', color=color.white)
    e.model.colorize()
    # camera.position=(20,20,-20)
    ec = EditorCamera(rotation_smoothing=2, rotation_speed=200)
    # camera.look_at(ec)

    rotation_info = Text(position=window.top_left)

    def update():
        rotation_info.text = str(int(ec.pivot.rotation_y)) + '\n' + str(int(ec.pivot.rotation_x))

    app.run()
