from ursina import *

class EditorCamera(Entity):

    def __init__(self, **kwargs):
        super().__init__(name='editor_camera', eternal=True)

        camera.world_parent = self
        self.rotation_speed = 100
        self.pan_speed = (4, 4)
        self.move_speed = 1
        self.zoom_speed = .05
        self.rotate_around_mouse_hit = True

        for key, value in kwargs.items():
            setattr(self, key, value)



    def input(self, key):
        if key == '+':
            camera.fov += 1
            printvar(camera.fov)
        elif key == '-':
            camera.fov -= 1
            printvar(camera.fov)

        elif key == 'p':
            camera.orthographic = not camera.orthographic


        elif key == 'scroll up':
            target_position = Vec3(0,0,0)
            if mouse.hovered_entity and not mouse.hovered_entity.has_ancestor(camera):
                target_position = mouse.hovered_entity.world_position

            camera.world_position = lerp(camera.world_position, target_position, self.zoom_speed)

        elif key == 'scroll down':
            camera.world_position += camera.back * self.zoom_speed * 100


        elif key == 'right mouse down' or key == 'middle mouse down':
            if mouse.hovered_entity and self.rotate_around_mouse_hit:
                org_pos = camera.world_position
                self.world_position = mouse.world_point
                camera.world_position = org_pos


    def update(self):
        if mouse.right:
            self.rotation_x -= mouse.velocity[1] * self.rotation_speed
            self.rotation_y += mouse.velocity[0] * self.rotation_speed

            self.position += camera.right * held_keys['d'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt']))
            self.position += camera.left * held_keys['a'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt']))
            self.position += camera.forward * held_keys['w'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt']))
            self.position += camera.back * held_keys['s'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt']))
            self.position += camera.up * held_keys['e'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt']))
            self.position += camera.down * held_keys['q'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt']))


        if mouse.middle:
            self.position -= camera.right * mouse.velocity[0] * self.pan_speed[0]
            self.position -= camera.up * mouse.velocity[1] * self.pan_speed[1]



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
        rotation_info.text = str(int(ec.rotation_y)) + '\n' + str(int(ec.rotation_x))

    app.run()
